"""Typed run-local runtime identity/value store with explicit observation provenance."""
import copy
import uuid

class IdentityConflict(ValueError): pass

class RTV:
    def __init__(self,run_id):
        self.run_id=run_id;self.records={};self.aliases={};self.symbols={};self.history=[];self.edges=[]

    @staticmethod
    def scope_key(scope):
        return tuple(sorted(scope.items()))

    @staticmethod
    def normalize(kind,value):
        if value is None or isinstance(value,bool): raise ValueError('Invalid identity value')
        if kind=='id' and isinstance(value,str):
            try: return ('uuid',str(uuid.UUID(value)))
            except ValueError: pass
        if isinstance(value,(dict,list)): raise ValueError('Identity value must be scalar')
        return (type(value).__name__,value)

    def alias_key(self,entity,scope,kind,value):
        return self.run_id,entity,self.scope_key(scope),kind,self.normalize(kind,value)

    def observe(self,entity,symbol,scope,identifiers,source,status=200,values=None):
        if not source or not 200 <= status < 300:
            raise ValueError('A successful, explicitly sourced observation is required')
        if not identifiers: raise ValueError('No identity evidence provided')
        keys={kind:self.alias_key(entity,scope,kind,value) for kind,value in identifiers.items()}
        symbol_key=(entity,self.scope_key(scope),symbol)
        existing={self.aliases[k] for k in keys.values() if k in self.aliases}
        if symbol_key in self.symbols: existing.add(self.symbols[symbol_key])
        if len(existing)>1: raise IdentityConflict('Observed aliases point to different instances')
        record_id=next(iter(existing)) if existing else 'instance-'+str(len(self.records)+1)
        prior=self.records.get(record_id)
        if prior:
            if prior['state']=='DELETED': raise IdentityConflict('A deleted instance cannot be revived without a new lifecycle')
            old_primary=prior['identifiers'].get('id');new_primary=identifiers.get('id')
            if old_primary is not None and new_primary is not None and self.normalize('id',old_primary)!=self.normalize('id',new_primary):
                raise IdentityConflict('A symbolic instance cannot change its primary identity')
            changed=[k for k,v in identifiers.items() if k in prior['identifiers'] and self.normalize(k,v)!=self.normalize(k,prior['identifiers'][k])]
            if changed and ('id' not in identifiers or 'id' not in prior['identifiers']):
                raise IdentityConflict('Alias rename requires matching primary-id evidence')
        # Validation above is transactional: a rejected observation changes no binding.
        if prior is None:
            self.records[record_id]={'entity_type':entity,'scope':dict(scope),'identifiers':{},'values':{},'state':'OBSERVED','symbols':[]}
        record=self.records[record_id]
        for kind,value in identifiers.items():
            if kind in record['identifiers'] and self.normalize(kind,value)!=self.normalize(kind,record['identifiers'][kind]):
                old_key=self.alias_key(entity,scope,kind,record['identifiers'][kind]);self.aliases.pop(old_key,None)
            record['identifiers'][kind]=value;self.aliases[keys[kind]]=record_id
        self.symbols[symbol_key]=record_id
        if symbol not in record['symbols']: record['symbols'].append(symbol)
        record['values'].update(values or {})
        self.history.append({'record_id':record_id,'source':source,'status':status,'identifiers':dict(identifiers)})
        return record_id

    def resolve(self,entity,scope,kind,value):
        record_id=self.aliases[self.alias_key(entity,scope,kind,value)]
        if self.records[record_id]['state']=='DELETED': raise KeyError('The instance was deleted')
        return record_id

    def mark_deleted(self,record_id,source,status):
        if not source or not 200 <= status < 300: raise ValueError('A successful deletion observation is required')
        self.records[record_id]['state']='DELETED'
        # Related edges become stale/unknown, not automatically proven absent.
        for edge in self.edges:
            if record_id in (edge['source'],edge['target']): edge['state']='STALE_AFTER_DELETE'
        self.history.append({'record_id':record_id,'source':source,'status':status,'state':'DELETED'})

    def observe_link(self,relation,source_id,target_id,source,status=200):
        if not source or not 200 <= status < 300: raise ValueError('A successful relationship observation is required')
        for record_id in (source_id,target_id):
            if record_id not in self.records or self.records[record_id]['state']=='DELETED':
                raise ValueError('The relationship endpoint is not a live observed instance')
        edge={'relation':relation,'source':source_id,'target':target_id,'evidence':source,'state':'OBSERVED'}
        if edge not in self.edges: self.edges.append(edge)

    def observe_unlink(self,relation,source_id,target_id,source,status=200):
        if not source or not 200 <= status < 300: raise ValueError('A successful relationship observation is required')
        for edge in self.edges:
            if (edge['relation'],edge['source'],edge['target'])==(relation,source_id,target_id):
                edge['state']='ABSENCE_OBSERVED';edge['evidence']=source

    def export(self):
        return copy.deepcopy({'run_id':self.run_id,'records':self.records,'observations':self.history,'observed_edges':self.edges})
