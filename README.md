# PluhDrive.
## Core Plan
The core plan for this project is a simple file sharing software, which can run locally on a server, for a set of clients set for it. A user will use a Terminal User Interface (TUI) to interact with the software, by inputing the IP Address of the server, and requesting files. Within the servers, the users will be able to make accounts and have their own file systems, similar to google drive. This is the main difference between this, and your stand alone file sharing sites like (transfer.zip). All data, for scalability, will be stored in a SQL database, which houses the filesystem and manifests for each file. Each "file manifest" contains metadata about each file, time created, owner, and a hash for the file, serving as the file identifier. This entire system will be hooked up to an API, using ```fastapi```, which has a RESTful API for communication between the server and clients. All commands in specifications will be valid to change or edit the filesystems.

## Specifications
The core idea is a simple filesharing code that allows quick sending and receiving of files from the cloud. The backend uses sql to manage each users
filesystem, info manifests and other. The actual code can be altered by the server administrator. The commands are as follows:
 - `mkuser`: Create a new user account. Needs: ✅
   - `username`: user's name; fs are hidden for other users on the network
   - `password`: user's password
 - `listusrs`: List all users ✅
 - `login`: Login to an existing user account. Needs: ✅
   - `username`: user's name
   - `password`: user's password (optional for admins)
 - `ls`: List the contents of the current directory ✅
   - `uid`: user's id
   - `path`: path to directory.
 - `mkdir`: Create a new directory ✅
   - `uid`: user's id
   - `path`: path to directory.
 - `rm`: Remove a file or directory
   - `uid`: user's id
   - `path`: path to file or directory.
 - `mv`: Copy File into new directory, and delete the orginal ✅
   - `uid`: user's id
   - `src`: source path
   - `dst`: destination path
 - `cp`: Copy a file or directory ✅
   - `uid`: user's id
   - `src`: source path
   - `dst`: destination path
 - `info`: Get manifest about a file
   - `uid`: user's id
   - `path`: path to file
 - `exit`: Exit the program ✅
 - `create`: Create a new file manifest
   - `uid`: user's id
   - `path`: path to file manifest
   - `content`: content of the file manifest
 - `create`: makes a new file manifest ✅
   - `uid`: user's id
   - `path`: path to file manifest
   - `content`: content of the file manifest
 - `delete`: marks the file as deleted
   - `uid`: user's id
   - `path`: path to file manifest

The idea is one day this is turned into an **API**, so that people can create UI's for this.

## Instalation
> nothing
