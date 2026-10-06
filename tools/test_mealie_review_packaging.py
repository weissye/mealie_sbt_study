import tempfile, unittest, zipfile
from pathlib import Path
from run_mealie_generator_live import bundle_review

class PackagingTests(unittest.TestCase):
    def test_excludes_authentication_products_retains_model_and_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ['model/products/internal/auth.json','model/products/internal/runs-db.db','model/spec/js/stories.mealie.js','acceptance-report.json','live-output.txt','samples.json']:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
            bundle_review(root)
            bundle_review(root)
            with zipfile.ZipFile(root/'review.zip') as archive:
                self.assertEqual(set(archive.namelist()),{'model/spec/js/stories.mealie.js','acceptance-report.json','live-output.txt','samples.json'})
                self.assertIsNone(archive.testzip())
if __name__=='__main__':unittest.main()
