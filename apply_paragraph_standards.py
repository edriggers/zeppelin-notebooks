import glob
import json
import yaml
import argparse
import sys
from pprint import pprint
from dateutil import parser

"""Splice Machine is building Apache Zeppelin Notebooks as part of its
training and product marketing efforts.  The Notebooks are primarily edited
using the Apache Zeppelin application itself.  There are some shortcomings in
the UI of this relatively young product that don't allow the user to set
some settings that are available in the underlying JSON data files.  One such
example is resetting the "READY"/"FINISHED"/"ERROR" status after testing a
paragraph's RUN feature.  Another is removing the "time taken" output from the
paragraph in the notebook.

The script has two separate operations that it will perform.  The first is a
"repair" type operation, in which it will apply our standardization changes to
each paragraph object and optionally write back those changes to the original
note.json files.  The second is a "reporting" option which will be used to
identify potentially saved "editor" data that hasn't been rendered into
"results" data.  As the "editor" code is "Run" inside of Apache Zeppelin and
saved in a "results" object in the JSON as rendered HTML.  So it is possible
to create content in Markdown style paragraphs and NOT Run them, in which
case outdated content would be displayed.  This second operation hasn't been
fully implemented/tested and is future intended as a potential process to run
in a Jenkins job triggered by the push to a branch of the splicemachine
zeppelin-notebooks repository on GitHub.

-t, --tests {All|MDTimeCheck|CodeBlockFix}
    CodeBlockFix is the "repair" mode.
    MDTimeCheck is the "report" mode.
-m, --modify switch will write changes back to the note.json files.

This script will recursively loop through all of the directories under the
working directory and load all of the note.json files in the notebook
directories and process each of the paragraphs inside the notebooks.  Each
paragraph will have a set of standards applied based upon the
'config'/'editorMode' section of the JSON for a paragraph object.

There is an "exceptions" methodology that is being defined in the
'notebook_standards_exceptions.yaml' file.

The primary thoughts initially driving this script:

1.  There are two primary types of paragraphs being used.  Markdown and Code
2.  Markdown paragraphs are descriptive content of our notebooks.
    a.  The "editor" should normally be hidden and only the rendered content
        displayed.
    b.  The "run" button should not be visible.
    c.  The status of these blocks should read "FINISHED"
3.  Code paragraphs are the scripting examples of our notebooks.
    a.  The rendered "results" should be cleared.
    b.  The "run" button should be visible.
    c.  The "editor" should be visible.
    d.  The status of these blocks should read "READY"

Potentially there will be additional standard settings, like setting a
"language" for a Code based paragraph so that the syntax highlighting will be
correct.  These would be specific to a 'config'/'editorMode' type.
"""


def increment(x):
    return x + 1


def decrement(x):
    return x - 1


def log_line(log_data):
    """Standardize the log output making it easier to scan through

    Arguments:
    logdata   -- array of the following data
                 notebook_id, paragraph #, paragraph title, log text
    """

    print("{:<10} pg#{:<2} {:<40} {:<25}".format(log_data[0],
          log_data[1], log_data[2][:40], log_data[3]))


def get_exception_detail(notebook_id, paragraph_id,
                         field_name, exceptions):
    """Validate if the specified field for the paragraph has an exception
    listed and return the details.
    """

    exception_detail = None
    # handle exceptions, apply these last
    if notebook_id in exceptions['Exceptions']:
        if paragraph_id in exceptions['Exceptions'][notebook_id]:
            p_except = exceptions['Exceptions'][notebook_id][paragraph_id]
            if field_name in p_except:
                exception_detail = p_except[field_name]

    return exception_detail


def repair_other_paragraph_block(paragraph, tracking):
    """This routine is called when no defined 'editorMode' is found in the
    paragraph.  We will apply a standard set of settings to paragraphs with an
    unhandled 'editorMode' type.

    Arguments:
    paragraph       -- this is a single 'Paragraph' JSON block from the
                       original data file.
    tracking        -- this is our set of tracking variables, used to avoid
                       global variable contamination
    """

    paragraph_title = paragraph.get('title', 'empty title')

    if paragraph['text'].startswith('%md'):
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "Editor NOT CODE"])

    if paragraph['config'].get('editorHide', False):
        log_line([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "Editor IS HIDDEN"])
        if tracking['modify']:
            paragraph['config']['editorHide'] = False
            tracking['has_changes'] = True

    if paragraph['config'].get('tableHide', False):
        log_line([tracking['notebook_id'], tracking['para_count'],
                    paragraph_title, "Table IS HIDDEN"])
        if tracking['modify']:
            paragraph['config']['tableHide'] = False
            tracking['has_changes'] = True

    if not paragraph['config'].get('enabled', False):
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "Run Button IS DISABLED"])
        if tracking['modify']:
            paragraph['config']['enabled'] = True
            tracking['has_changes'] = True

    if 'results' in paragraph and 'msg' in paragraph['results']:
        msg = paragraph['results']
        msg.pop('msg', None)
        tracking['has_changes'] = True
        if 'dateStarted' in paragraph and 'dateFinished' in paragraph:
            log_line([tracking['notebook_id'], tracking['para_count'],
                        paragraph_title, "Results ARE STORED"])
            if tracking['modify']:
                paragraph.pop('dateStarted', None)
                paragraph.pop('dateFinished', None)

    if paragraph.get('status', '') != 'READY':
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "Paragraph NOT READY"])
        if tracking['modify']:
            paragraph['status'] = 'READY'
            tracking['has_changes'] = True


def repair_md_paragraph_block(paragraph, tracking, test_exceptions):
    """This routine is called on paragraph blocks with an 'editorMode' of
    /ace/mode/markdown.
    This will set defaults in the original paragraph JSON to match what we want
    for MD block types.

    Arguments:
    paragraph       -- this is a single 'Paragraph' JSON block from the
                       original data file.
    tracking        -- this is our set of tracking variables, used to avoid
                       global variable contamination
    test_exceptions -- this is our YAML data for data overrides, currently
                       only being used for the MD blocks.
    """

    paragraph_title = paragraph.get('title', 'empty title')

    editor_open_override = get_exception_detail(
        tracking['notebook_id'], paragraph['id'],
        'MarkdownEditorOpen', test_exceptions
    )

    if not paragraph['text'].startswith('%md'):
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "%md NOT MARKDOWN EDITOR"])

    if paragraph['config'].get('enabled', False):
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "%md Run Button IS ENABLED"])
        if tracking['modify']:
            paragraph['config']['enabled'] = False
            tracking['has_changes'] = True

    if paragraph.get('status', '') == "READY":
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "%md Status IS READY"])
        if tracking['modify']:
            paragraph['status'] = 'FINISHED'
            tracking['has_changes'] = True

    if not paragraph['config'].get('editorHide', False):
        log_line([tracking['notebook_id'], tracking['para_count'],
                    paragraph_title, "Editor NOT HIDDEN"])
        if tracking['modify']:
            paragraph['config']['editorHide'] = True
            tracking['has_changes'] = True

    if paragraph['config'].get('tableHide', False):
        log_line([tracking['notebook_id'], tracking['para_count'],
                    paragraph_title, "Table IS HIDDEN"])
        if tracking['modify']:
            paragraph['config']['tableHide'] = False
            tracking['has_changes'] = True

    if editor_open_override is not None:
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "%md Editor OVERRIDE, IGNORE ABOVE"])
        paragraph['config']['editorHide'] = False
        paragraph['config']['enabled'] = True
        paragraph['status'] = 'READY'
        tracking['has_changes'] = True


def report_md_paragraph_block(paragraph, tracking):
    """This routine is soley for reporting.  The paragraph block JSON
    contains a 'text' field, and a 'results/data' field.  The 'text' field is
    the 'source' and the 'results/data' field is the rendered data.  There are
    several 'date' type fields that track updates.  'dateUpdated' tracks
    updates/saves to the 'text' field, and 'dateStarted'/'dateFinished' tracks
    details about the 'results/data' field.  It makes sense that if the
    'dateUpdated' is more recent than 'dateFinished' then the rendered output
    in 'results/data' should be out of date.  I don't know if we will be able
    to correct this using an external script as
    the rendering is part of the 'run' feature of Zeppelin Notebooks.  However,
    my thought is that we could potentially use this as part of a 'lint' test
    upon checking in a branch and launching a Jenkins job to run the lint test
    and reporting back into github that the push to the branch passes.

    Arguments:
    paragraph       -- this is a single 'Paragraph' JSON block from the
                       original data file.
    tracking        -- this is our set of tracking variables, used to avoid
                       global variable contamination
    """

    paragraph_title = paragraph.get('title', 'empty title')

    updated = parser.parse(paragraph.get('dateUpdated',
                           '1970-01-01 00:00:00.000'))

    if 'dateFinished' in paragraph:
        finished = parser.parse(paragraph['dateFinished'])
    elif 'dateCreated' in paragraph:
        finished = parser.parse(paragraph['dateCreated'])
    else:
        finished = parser.parse('1970-01-01 00:00:00.000')

    if updated > finished:
        timediff = updated - finished
        diffminutes = timediff.total_seconds() // 60
        if tracking['tests'] in ['All', 'Report'] and diffminutes > 5:
            log_line([tracking['notebook_id'], tracking['para_count'],
                     paragraph_title, "Paragraph SAVED AFTER RUN" +
                     str(diffminutes)])
            print('        Saved:  ' + str(updated))
            print('    Generated:  ' + str(finished))


def process_paragraph(paragraph, tracking, test_exceptions):
    """This is the main call that is made for each paragraph being looped
    through in the main program.  We parse the 'config/editorMode' of the
    paragraph and send the paragraph down the line for further processing.

    'ace/mode/markdown', others

    The 'config/editorMode' isn't always set correctly, so this value can vary
    considerably even within a single interpreter type.  We are mostly
    concerned with the Markdown %md types, with all others being configured
    as 'execution' type paragraphs.  As we extend this and get the
    'config/editorMode' settings corrected we can then create some additional
    routines to be called to set things line 'editorSettings/language' and
    other specific features.

    Arguments:
    paragraph       -- this is a single 'Paragraph' JSON block from the
                       original data file.
    tracking        -- this is our set of tracking variables, used to avoid
                       global variable contamination
    test_exceptions -- this is our YAML data for data overrides, currently
                       only being used for the MD blocks.
    """

    paragraph_title = paragraph.get('title', 'empty title')

    editor_mode_override = get_exception_detail(
        tracking['notebook_id'], paragraph['id'],
        'EditorMode', test_exceptions
    )

    if editor_mode_override is not None:
        paragraph['config']['editorMode'] = editor_mode_override
        log_line([tracking['notebook_id'], tracking['para_count'],
                  paragraph_title, "EditorMode OVERRIDE"])

    if 'editorMode' in paragraph['config']:
        if paragraph['config']['editorMode'] == 'ace/mode/markdown':
            if tracking['tests'] in ['Report', 'All']:
                report_md_paragraph_block(paragraph, tracking)

            if tracking['tests'] in ['Repair', 'All']:
                repair_md_paragraph_block(paragraph, tracking, test_exceptions)

        elif paragraph['config']['editorMode'] == 'ace/mode/sql':
            # splicemachine blocks
            if tracking['tests'] in ['Repair', 'All']:
                # currently we are calling the 'other' format routine as we
                # have not identified the individual 'editorMode' features to
                # set.  This elif block is simply a placeholder for the next
                # iteration of the script
                repair_other_paragraph_block(paragraph, tracking)
        else:
            # all other blocks
            if tracking['tests'] in ['Repair', 'All']:
                repair_other_paragraph_block(paragraph, tracking)
    else:
        log_line([tracking['notebook_id'], tracking['para_count'],
                 paragraph_title, "Paragraph NO EDITORMODE"])


def main():
    """This routine will process the command line arguments and loop through
    all the note.json files in all subdirectories from the directory of
    execution.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--modify",
                        help="switch to turn on writing back to note.json",
                        action="store_true")
    parser.add_argument("-t", "--tests",
                        help="Specify the type of test being run",
                        type=str, choices=['Report', 'Repair', 'All'])

    try:
        args = parser.parse_args()
    except SystemExit:
        # the unfortunate trade off here is that even a successful -h run
        # will raise "SystemExit" in order to terminate the execution, and
        # there doesn't seem to be an easy way to determine the difference
        # between a successful -h call, and a call with bad arguments.
        # When running under a Jenkins job, we most certainly want to return
        # a non-zero if the script hasn't run for any reason.
        return 1

    track_vars = {
        'modify': args.modify,
        'tests': args.tests or "Repair",
        'has_changes': False,
        'para_count': 1,
        'notebook_id': "",
        'status': 0
    }

    # get our standards exceptions loaded
    with open("./notebook_standards_exceptions.yaml", 'r') as stream:
        sanity_exceptions = yaml.load(stream)

    # load and loop through the notebook json files.
    note_files = glob.glob('./**/note.json')
    for note_file in note_files:
        track_vars['has_changes'] = False
        with open(note_file, 'r+') as file_handler:
            track_vars['notebook_id'] = note_file.split('/')[1]
            data = json.load(file_handler)
            # We will start at normal counting, so when you load the notebook,
            # you can simply count to match with the reported paragraph number.
            # some notebook paragraphs have a 'title' set, at some point when
            # that is more populated we can switch to referring to the
            # paragraphs by title instead throughout.  For now paragraph
            # counting will have to be sufficient.
            track_vars['para_count'] = 1
            for notebook_paragraph in data['paragraphs']:
                process_paragraph(notebook_paragraph,
                                  track_vars, sanity_exceptions)
                track_vars['para_count'] = track_vars['para_count'] + 1
            if track_vars['modify'] and track_vars['has_changes']:
                print("Saving " + track_vars['notebook_id'])
                try:
                    file_handler.seek(0)
                    json.dump(data, file_handler, indent=2, sort_keys=False)
                    file_handler.truncate()
                except:
                    print("An error occurred while writing to " + note_file)
                    track_vars['status'] = 1
    return track_vars['status']


# Call the main Routine
sys.exit(main())
