import glob
import json
import yaml
import getopt
import sys
from pprint import pprint
from dateutil import parser


def usage():
    """Print the standard usage for calling the script.
    Outputs valid options.

    Arguments: none
    """

    print('Usage:')
    print("\t -m                       : modify source files")
    print("\t -t:{test}, --test {test} : run specific tests, or All (default)")
    print("\t -h, or --help            : display help")
    print("\t Test list:")
    print("\t\t All")
    print("\t\t MDTimeCheck")
    print("\t\t CodeBlockFix")


def logline(logdata):
    """Standardize the log output making it easier to scan through

    Arguments:
    logdata   -- array of the following data
                 notebook_id, paragraph #, paragraph title, log text
    """

    print("{:<10} pg#{:<2} {:<40} {:<25}".format(logdata[0],
          logdata[1], logdata[2][:40], logdata[3]))


def get_exceptiondetail(notebook_id, paragraph_id,
                        field_name, exceptions_list):
    """Validate if the specified field for the paragraph has an exception
    listed and return the details.
    """
    exception_detail = {}
    exception_detail['exists'] = False
    exception_detail['value'] = None

    # handle exceptions, apply these last
    if notebook_id in exceptions_list['Exceptions']:
        if paragraph_id in exceptions_list['Exceptions'][notebook_id]:
            p_except = exceptions_list['Exceptions'][notebook_id][paragraph_id]
            if field_name in p_except:
                exception_detail['exists'] = True
                exception_detail['value'] = p_except[field_name]

    return exception_detail


def test_othercodeblockfix(paragraph, tracking):
    """This routine is called when no defined 'editorMode' is found in the
    paragraph.  We will apply a standard set of settings to paragraphs with an
    unhandled 'editorMode' type.

    Arguments:
    paragraph       -- this is a single 'Paragraph' JSON block from the
                       original data file.
    tracking        -- this is our set of tracking variables, used to avoid
                       global variable contamination
    """

    paragraph_title = 'empty title'
    if 'title' in paragraph:
        paragraph_title = paragraph['title']

    if paragraph['text'].startswith('%md'):
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "Editor NOT MARKDOWN"])

    if 'editorHide' in paragraph['config']:
        if paragraph['config']['editorHide']:
            logline([tracking['notebook_id'], tracking['para_count'],
                    paragraph_title, "Editor IS HIDDEN"])
            if tracking['modify']:
                paragraph['config']['editorHide'] = False
                tracking['has_changes'] = True

    if 'tableHide' in paragraph['config']:
        if paragraph['config']['tableHide']:
            logline([tracking['notebook_id'], tracking['para_count'],
                    paragraph_title, "Table IS HIDDEN"])
            if tracking['modify']:
                paragraph['config']['tableHide'] = False
                tracking['has_changes'] = True

    if 'enabled' in paragraph['config'] and not paragraph['config']['enabled']:
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "Run Button IS DISABLED"])
        if tracking['modify']:
            paragraph['config']['enabled'] = True
            tracking['has_changes'] = True

    if 'results' in paragraph and 'msg' in paragraph['results']:
        msg = paragraph['results']
        msg.pop('msg', None)
        tracking['has_changes'] = True
        if 'dateStarted' in paragraph:
            if 'dateFinished' in paragraph:
                logline([tracking['notebook_id'], tracking['para_count'],
                        paragraph_title, "Results ARE STORED"])
                if tracking['modify']:
                    paragraph.pop('dateStarted', None)
                    paragraph.pop('dateFinished', None)

    if paragraph['status'] != 'READY':
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "Paragraph NOT READY"])
        if tracking['modify']:
            paragraph['status'] = 'READY'
            tracking['has_changes'] = True


def test_mdcodeblockfix(paragraph, tracking, test_exceptions):
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

    paragraph_title = 'empty title'
    if 'title' in paragraph:
        paragraph_title = paragraph['title']

    editoropen_override = get_exceptiondetail(
        tracking['notebook_id'], paragraph['id'],
        'MarkdownEditorOpen', test_exceptions
    )

    if not paragraph['text'].startswith('%md'):
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "%md NOT MARKDOWN EDITOR"])

    if 'enabled' in paragraph['config'] and paragraph['config']['enabled']:
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "%md Run Button IS ENABLED"])
        if tracking['modify']:
            paragraph['config']['enabled'] = False
            tracking['has_changes'] = True

    if 'status' in paragraph and paragraph['status'] == "READY":
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "%md Status IS READY"])
        if tracking['modify']:
            paragraph['status'] = 'FINISHED'
            tracking['has_changes'] = True

    if 'editorHide' in paragraph['config']:
        if not paragraph['config']['editorHide']:
            logline([tracking['notebook_id'], tracking['para_count'],
                    paragraph_title, "Editor NOT HIDDEN"])
            if tracking['modify']:
                paragraph['config']['editorHide'] = True
                tracking['has_changes'] = True

    if 'tableHide' in paragraph['config']:
        if paragraph['config']['tableHide']:
            logline([tracking['notebook_id'], tracking['para_count'],
                    paragraph_title, "Table IS HIDDEN"])
            if tracking['modify']:
                paragraph['config']['tableHide'] = False
                tracking['has_changes'] = True

    if editoropen_override['exists']:
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "%md Editor OVERRIDE, IGNORE ABOVE"])
        paragraph['config']['editorHide'] = False
        paragraph['config']['enabled'] = True
        paragraph['status'] = 'READY'
        tracking['has_changes'] = True


def test_mdblockgeneration(paragraph, tracking):
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

    paragraph_title = 'empty title'
    if 'title' in paragraph:
        paragraph_title = paragraph['title']

    updated = parser.parse('1970-01-01 00:00:00.000')
    if 'dateUpdated' in paragraph:
        updated = parser.parse(paragraph['dateUpdated'])

    if 'dateFinished' in paragraph:
        finished = parser.parse(paragraph['dateFinished'])
    elif 'dateCreated' in paragraph:
        finished = parser.parse(paragraph['dateCreated'])
    else:
        finished = parser.parse('1970-01-01 00:00:00.000')

    if updated > finished:
        timediff = updated - finished
        diffminutes = divmod(timediff.total_seconds(), 60)[0]
        if tracking['tests'] == 'All' or tracking['tests'] == 'MDTC':
            if diffminutes > 5:
                logline([tracking['notebook_id'], tracking['para_count'],
                        paragraph_title, "Paragraph SAVED AFTER RUN" +
                        str(diffminutes)])
                print('        Saved:  ' + str(updated))
                print('    Generated:  ' + str(finished))


def test_paragraph(paragraph, tracking, test_exceptions):
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

    paragraph_title = 'empty title'
    if 'title' in paragraph:
        paragraph_title = paragraph['title']

    editormode_override = get_exceptiondetail(
        tracking['notebook_id'], paragraph['id'],
        'EditorMode', test_exceptions
    )

    if editormode_override['exists']:
        paragraph['config']['editorMode'] = editormode_override['value']
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "EditorMode OVERRIDE"])
    if 'editorMode' in paragraph['config']:
        if paragraph['config']['editorMode'] == 'ace/mode/markdown':
            if tracking['tests'] == 'MDTC' or tracking['tests'] == 'All':
                test_mdblockgeneration(paragraph, tracking)

            if tracking['tests'] == 'CBF' or tracking['tests'] == 'All':
                test_mdcodeblockfix(paragraph, tracking, test_exceptions)

        elif paragraph['config']['editorMode'] == 'ace/mode/sql':
            # splicemachine blocks
            if tracking['tests'] == 'CBF' or tracking['tests'] == 'All':
                # currently we are calling the 'other' format routine as we
                # have not identified the individual 'editorMode' features to
                # set.  This elif block is simply a placeholder for the next
                # iteration of the script
                test_othercodeblockfix(paragraph, tracking)
        else:
            # all other blocks
            if tracking['tests'] == 'CBF' or tracking['tests'] == 'All':
                test_othercodeblockfix(paragraph, tracking)
    else:
        logline([tracking['notebook_id'], tracking['para_count'],
                paragraph_title, "Paragraph NO EDITORMODE"])


def main(incoming_args):
    """This routine will process the command line arguments and loop through
    all the note.json files in all subdirectories from the directory of
    execution.

    Arguments:
    incoming_args -- This value comes from the sys.argv variable
    """
    try:
        parsed_options, parsed_args = getopt.getopt(
            incoming_args, "-t:hm", ["help", "test=", "--modify"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(1)

    with open("./NotebookSanityExceptions.yaml", 'r') as stream:
        sanity_exceptions = yaml.load(stream)

    track_vars = {}
    track_vars['modify'] = False
    track_vars['tests'] = 'All'
    track_vars['has_changes'] = False
    track_vars['para_count'] = 1
    track_vars['notebook_id'] = ""
    track_vars['status'] = 0

    for options, option_args in parsed_options:
        if options in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif options in ("-t", "--test"):
            if option_args.lower() == 'all':
                track_vars['tests'] = 'All'
            elif option_args.lower() == 'mdtimecheck':
                track_vars['tests'] = 'MDTC'
            elif option_args.lower() == 'codeblockfix':
                track_vars['tests'] = 'CBF'
        elif options in ("-m", "--modify"):
            track_vars['modify'] = True
        else:
            assert False, "unhandled option: " + options + \
                ", option arguments (" + option_args + ")"
        if len(parsed_args) > 0:
            print("stand alone arguments have been ignored: ")
            for ignored_arg in parsed_args:
                print("\t" + ignored_arg)

    notefiles = glob.glob('./**/note.json')

    for note_file in notefiles:
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
                test_paragraph(notebook_paragraph,
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
exitcode = 0
exitcode = main(sys.argv[1:])
sys.exit(exitcode)
