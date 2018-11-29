# Splice Machine Training Notebooks

This is the repository for the Zeppelin notebooks used for Splice Machine Training. These notebooks can be loaded into Zeppelin running on your standalone, or they can be built into a docker image.

## Using the Notebooks with the Apache Zeppelin Distribution
To use the notebooks in this repo with a locally installed version of Apache Zeppelin, follow these steps:

1. Navigate to the [Apache Zeppelin web site](https://zeppelin.apache.org/).
2. Click the *Download* button and download the Zeppelin tarball; for example: `zeppelin-0.8.0-bin-all.tgz`.
3. Move the download to a location from which you want to run Zeppelin.
4. Unpack the tarball, which will create a new subdirectory, e.g. `zeppelin-0.8.0-bin-all`.
5. `cd zeppelin-0.8.0-bin-all/notebook`
6. You can optionally delete all of the notebooks that are shipped with Zeppelin (recommended).
6. Copy the contents of this repo to the `notebook` folder. There should be 43 notebooks, plus the `datasets_for_python_notebook` folder.
7. `cd zeppelin-0.8.0-bin-all/bin`
8. Run `zeppelin.sh`
9. Point your browser to localhost:8080

The notebooks in this repo will be organized into the `Splice Machine Training` folder, which contains a subfolder for each of our training classes.

### Updating the Repo
After modifying the notebooks in your local version of Zeppelin, update your local repo by copying all of the notebook folders in the `zeppelin-0.8.0-bin-all/notebook` folder into the local version of your notebooks repo.

## Using the Notebooks with the Splice Training Docker Image

To use the notebooks in this repo with the docker image distributed by Splice Machine:

1. Run docker on your computer.
2. In the docker Advanced Preferences, set memory to 12GB.
3. Start the Splice Machine docker container with this command:
   `docker run -ti  --sysctl net.ipv6.conf.all.disable_ipv6=1  --name spliceserver  --hostname localhost  -p 1527:1527 -p 4040:4040 -p 7078:7078  -p 8080:8080 -p 8090:8090 -p 8091:8091  splicemachine/standalone:latest`
4. Once the container starts, you'll see a command prompt. Issue these commands in sequence:
   ```
   ./start-spark-master.sh
   ./start-spark-slave.sh
   ./start-splice.sh
   ./start-zeppelin.sh
   ```

   Note that the `./start-splice.sh` step will take a couple minutes, and you may see a sequence of warnings displayed; you can ignore these messages while the various services are starting up:
   `Ncat: Cannot assign requested address.`

   The `./start-zeppelin.sh` step will also display some warning messages that you can ignore.

5. You can then browse to `localhost:8090` to work with the Training notebooks.

## Tracking Notebooks
Because Zeppelin *names* notebooks with non-descriptive IDs, we've created a spreadsheet that maps notebook descriptions to their IDs, and tracks which notebook is the next-in-sequence in each course. [This Google Sheets spreadsheet](https://docs.google.com/spreadsheets/d/1IwCkolUBSRxK5gTjOxpm3Wu7QfikHv1O7xLkkD7FFk8/edit?usp=sharing) contains a sheet for each of our courses.

### Adding and Deleting Notebooks

Our training courses include duplicate (or almost duplicate) versions of various, which share the same descriptive names. Because of this, it's important to maintain the mappings and next-in-sequence links in the spreadsheet.

If you add a notebook to a course, you'll need to add it to the appropriate spreadsheet tab. And you'll need to modify the next-in-sequence notebook link that is found in the `Where to Go Next` section at the bottom of each training notebook:

* Edit the notebook that will precede the new notebook in the course sequence.
* Copy the next-in-sequence link information in that notebook to your clipboard.
* Modify that link to point to the new notebook.
* Edit the new notebook and paste the next-in-sequence information into the `Where to Go Next` section.
* You'll also need to rename (by changing the notebook lowercase-alpha "prefix") any notebooks that follow the newly inserted notebook. Renaming is easily done from the Zeppelin home page.
  For example, if you insert a new notebook between "c. Running Queries" and "d. Tuning Queries", you'll need to prefix the new notebook with "d.", rename the next notebook to "e. Tuning Queries", and then similarly change the prefix on each subsequent notebook.
* Update the spreadsheet tab with info about the new notebook, AND update the prefix in each name in the spreadsheet tab.

If you going to delete a notebook from a course, you'll need to update the spreadsheet tab for that course, and:

* Edit the notebook you're about to delete.
* Copy the next-in-sequence link information in that notebook to your clipboard.
* Edit the notebook that precedes the one that you're deleting in the course sequence and modify its next-in-sequence link information by pasting in the link info from the clipboard.
* You'll also need to rename (by changing the notebook lowercase-alpha "prefix") any notebooks that follow the newly deleted notebook. Renaming is easily done from the Zeppelin home page.
  For example, if you delete a notebook named "d. Tuning Queries", you'll need to prefix the next ("e. ") notebook with "d.",  and then similarly change the prefix on each subsequent notebook.
* Update the spreadsheet tab with info about the new notebook, AND update the prefix in each name in the spreadsheet tab.
