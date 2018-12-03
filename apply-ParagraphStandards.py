import glob
import json
import yaml
import getopt, sys
from pprint import pprint
from dateutil import parser

def usage():
    print ('Usage:')
    print ("\t -m                               : modify source files")
    print ("\t -t:{test}, or --test {test}      : run specific tests, or All (default)")
    print ("\t -h, or --help                    : display help")
    print ("\t Test list:")
    print ("\t\t All")
    print ("\t\t MDBlockGeneration")
    print ("\t\t CodeBlockFix")

try:
    opts, args = getopt.getopt(sys.argv[1:], "-t:hm", ["help", "test=", "--modify"])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
modify = False
tests = "All"
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-t", "--test"):
        if a.lower() == 'all':
            tests = 'All'
        elif a.lower() == 'mdblockgeneration':
            tests = 'MDBlockGeneration'
        elif a.lower() == 'codeblockfix':
            tests = 'CodeBlockFix'
    elif o in ("-m", "--modify"):
            modify = True
    else:
        assert False, "unhandled option"

with open("./NotebookSanityExceptions.yaml", 'r') as stream:
    sanity_exceptions = yaml.load(stream)

notefiles = glob.glob('./**/note.json')

for nf in notefiles:
    with open(nf, 'r+') as f:
        notebook_id = nf.split('/')[1]
        data = json.load(f)
        # We will start at normal counting, so when you load the notebook,
        # you can simply count to match with the reported paragraph number.
        x = 1
        for i in data['paragraphs']:
            if 'title' in i:
                paragraph_title = i['title']
            # MARKDOWN %md items
            if i['config']['editorMode'] == 'ace/mode/markdown':
                if tests.lower() == 'MDBlockGeneration' or tests == 'All':
                    if 'dateUpdated' in i:
                        updated = parser.parse(i['dateUpdated'])
                    if 'dateFinished' in i:
                        finished = parser.parse(i['dateFinished'])
                    else:
                        if 'dateCreated' in i:
                            finished = parser.parse(i['dateCreated'])
                        else:
                            finished = parser.parse('1970-01-01 00:00:00.000')
                    if updated > finished:
                        timediff = updated - finished
                        diffminutes = divmod(timediff.total_seconds(), 60)[0]
                        if tests == 'All' or tests == 'MDBlockGeneration':
                            if diffminutes > 5:
                                print (notebook_id + ': paragraph #' + str(x) + ' was saved ' + str(diffminutes) + ' minutes after being generated')
                                print ('        Saved:  ' + str(updated))
                                print ('    Generated:  ' + str(finished))
                if tests == 'CodeBlockFix' or tests == 'All':
                    if i['text'].startswith('%md') == False:
                        print (notebook_id + ': paragraph #' + str(x) + ' is set to markdown editor yet does not start with %md')
                    if 'enabled' in i['config']:
                        if i['config']['enabled'] == True:
                            print (notebook_id + ': paragraph #' + str(x) + ' has execution enabled')
                            if modify == True:
                                i['config']['enabled'] = False
                    if 'status' in i:
                        if i['status'] == "READY":
                            print (notebook_id + ': paragraph #' + str(x) + ' status is READY, should be FINISHED')
                            if modify == True:
                                i['status'] = 'FINISHED'
                    if 'editorHide' in i['config']:
                        if i['config']['editorHide'] == False:
                            print (notebook_id + ': paragraph #' + str(x) + ' Editor is NOT hidden')
                            if modify == True:
                                i['config']['editorHide'] = True
                    # handle exceptions, apply these last
                    if notebook_id in sanity_exceptions['Exceptions']:
                        if i['id'] in sanity_exceptions['Exceptions'][notebook_id]:
                            if 'MarkdownEditorOpen' in sanity_exceptions['Exceptions'][notebook_id][i['id']]:
                                if sanity_exceptions['Exceptions'][notebook_id][i['id']]['MarkdownEditorOpen'] == True:
                                    i['config']['editorHide'] = False
                                    i['config']['enabled'] = True
                                    i['status'] = 'READY'
            else:
                # all other paragraph editors
                if tests == 'CodeBlockFix':
                    if i['text'].startswith('%md'):
                        print (notebook_id + ': paragraph #' + str(x) + '(' + paragraph_title + ') Editor is set to something other than MARKDOWN.')
                    if 'editorHide' in i['config']:
                        if i['config']['editorHide'] == True:
                            print (notebook_id + ': paragraph #' + str(x) + '(' + paragraph_title + ') Editor IS hidden')
                            if modify == True:
                                i['config']['editorHide'] = False
                    if 'enabled' in i['config']:
                        if i['config']['enabled'] == False:
                            print (notebook_id + ': paragraph #' + str(x) + '(' + paragraph_title + ') Run button DISABLED')
                            if modify == True:
                                i['config']['enabled'] = True
                    if 'results' in i:
                        if 'msg' in i['results']:
                            if 'dateStarted' in i:
                                if 'dateFinished' in i:
                                    print (notebook_id + ': paragraph #' + str(x) + ' Results are STORED.')
                                    if modify == True:
                                        i.pop('dateStarted',None)
                                        i.pop('dateFinished',None)
                    if i['status'] != 'READY':
                        print (notebook_id + ': paragraph #' + str(x) + ' Paragraph not marked as READY.')
                        if modify == True:
                            i['status'] = 'READY'
            x = x + 1
        if modify == True:
            f.seek(0)
            json.dump(data, f, indent=2, sort_keys=False)
            f.truncate()
