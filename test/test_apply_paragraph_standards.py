import unittest
import json
import yaml
import apply_paragraph_standards

class Test_TestRepairParagraphBlocks(unittest.TestCase):

    # Run the following tests:
    #  - Hidden Editor
    #  - Hidden Table
    #  - Disabled Run Button
    #  - Stored Results / Started and Finished time
    #  - Status other than READY
    def test_repair_other_paragraph_block_test1(self):
        with open('./test/test1.json', 'r') as file_handler:
            data = json.load(file_handler)
            notebook_paragraph = data['paragraphs'][0]
            tracking = {
                'modify': True,
                'tests': 'Repair',
                'has_changes': False,
                'para_count': 1,
                'notebook_id': "2TESTPGDOC",
                'status': 0
            }
            apply_paragraph_standards.repair_other_paragraph_block(notebook_paragraph, tracking)
            self.assertEqual(notebook_paragraph['config'].get('editorHide', False), False)
            self.assertEqual(notebook_paragraph['config'].get('tableHide', False), False)
            self.assertEqual(notebook_paragraph['config'].get('enabled', False), True)
            self.assertEqual(notebook_paragraph['results'].get('msg', False), False)
            self.assertEqual(notebook_paragraph.get('dateStarted', False), False)
            self.assertEqual(notebook_paragraph.get('dateFinished', False), False)
            self.assertEqual(notebook_paragraph.get('status', ''), 'READY')
            self.assertEqual(tracking['has_changes'], True)

    # Run the following tests:
    #  - Enabled Run Button
    #  - Status other than FINISHED
    #  - Visible Editor
    #  - Hidden Table
    def test_repair_md_paragraph_block_test2(self):
        with open('./test/test2.json', 'r') as file_handler:
            data = json.load(file_handler)
            notebook_paragraph = data['paragraphs'][0]
            tracking = {
                'modify': True,
                'tests': 'Repair',
                'has_changes': False,
                'para_count': 1,
                'notebook_id': "2TESTPGDOC",
                'status': 0
            }
            # get our standards exceptions loaded
            with open("./test/test_empty_exceptions.yaml", 'r') as stream:
                sanity_exceptions = yaml.load(stream)

            apply_paragraph_standards.repair_md_paragraph_block(notebook_paragraph, tracking, sanity_exceptions)
            self.assertEqual(notebook_paragraph['config'].get('editorHide', False), True)
            self.assertEqual(notebook_paragraph['config'].get('tableHide', False), False)
            self.assertEqual(notebook_paragraph['config'].get('enabled', False), False)
            self.assertEqual(notebook_paragraph.get('status', ''), 'FINISHED')
            self.assertEqual(tracking['has_changes'], True)

    # Run the following tests:
    #  - Pass in an override for the EditorOpen
    def test_repair_md_paragraph_block_test3(self):
        with open('./test/test2.json', 'r') as file_handler:
            data = json.load(file_handler)
            notebook_paragraph = data['paragraphs'][0]
            tracking = {
                'modify': True,
                'tests': 'Repair',
                'has_changes': False,
                'para_count': 1,
                'notebook_id': "2TESTPGDOC",
                'status': 0
            }
            # get our standards exceptions loaded
            with open("./test/test_exceptions.yaml", 'r') as stream:
                sanity_exceptions = yaml.load(stream)

            apply_paragraph_standards.repair_md_paragraph_block(notebook_paragraph, tracking, sanity_exceptions)
            self.assertEqual(notebook_paragraph['config'].get('editorHide', False), False)
            self.assertEqual(tracking['has_changes'], True)


if __name__ == '__main__':
    unittest.main()
