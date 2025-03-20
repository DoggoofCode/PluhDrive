# PluhDrive.
## Specifications
The core idea is a simple filesharing code that allows quick sending and receiving of files from the cloud. The backend uses sql to manage each users
filesystem, info manifests and other. The actual code can be altered by the server administrator. The commands are as follows:
 - `mkuser`: Create a new user account. Needs:
   - `username`: user's name; fs are hidden for other users on the network
   - `password`: user's password
 - `login`: Login to an existing user account. Needs:
   - `username`: user's name
   - `password`: user's password (optional for admins)
 - `ls`: List the contents of the current directory
   - `uid`: user's id
   - `path`: path to directory.
 - `mkdir`: Create a new directory
   - `uid`: user's id
   - `path`: path to directory.
 - `rm`: Remove a file or directory
   - `uid`: user's id
   - `path`: path to file or directory.
 - `mv`: Copy File into new directory, and delete the orginal
   - `uid`: user's id
   - `src`: source path
   - `dst`: destination path
 - `cp`: Copy a file or directory
   - `uid`: user's id
   - `src`: source path
   - `dst`: destination path
 - `info`: Get manifest about a file
   - `uid`: user's id
   - `path`: path to file
 - `exit`: Exit the program
 - `create`: Create a new file manifest
   - `uid`: user's id
   - `path`: path to file manifest
   - `content`: content of the file manifest
 - `create`: makes a new file manifest
   - `uid`: user's id
   - `path`: path to file manifest
   - `content`: content of the file manifest
 - `delete`: marks the file as deleted
   - `uid`: user's id
   - `path`: path to file manifest

The idea is one day this is turned into an **API**, so that people can create UI's for this.

## Instalation
> nothing
