
![enter image description here](https://github.com/bradley101/knight/raw/master/knight.jpg)

Knight is a command line utility for doing basic CodeChef operations like problem submission, history, etc directly from the terminal. Trust me it helps 😀
# Parameters & Usage

    usage: knight [-h] [-n] [-l] [-s problem_code solution_location] [--history problem_code] [-u] [--config] [--logout]

 - `-h or --help` - Displays the standard help on usage and parameters
 - `-n or --nologin` - Performs certain operations that don't require you to log in (currently only `-l or --list-contests`)
 - `-s <problem code> <solution file> or  --submit <problem code> <solution file>` - Submit your solution file to the specified problem code.
 - `--history <problem code>` - Display your submission history for that problem in a prettier tabular format.
 - `-u or --user` - Display the currently configured user on **Knight**.
 - `--config` - Set another username and password for logging into Codechef.
 - `--logout` - Logs out the configured user on Codechef (if logged in)

Note: **Knight** uses sessions  so your previous login session is saved for later use.



# Installation

 - Linux & Unix systems - `$ pip install knight --upgrade`
 - Windows - `pip install knight --upgrade`
 
 For Windows users, you need to add installation directory to `PATH`. At the end of the installation, you'll be notified by a warning with a location/directory. Copy that location and add it to system's `PATH` variable.
 # Requirements
 
 - Python 3.x
 
 # Issues
 In case of some error  or exceptions, please find the log files under `HOME_DIR/.knight/logs/` and submit an issue on Github with the logs.
 It will really be of great help improving the user experience.
 
 # How to Contribute
 
 - Fork the repo.
 - Clone the repo `https://github.com/<your username>/knight.git` to empty directory.
	 
    ```
    mkdir knight
    cd knight
    git clone https://github.com/<your username>/knight.git
    ```
    
 - Create a new branch for your changes.
	 ```
	 git branch my_branch
	 git checkout my_branch
	 ```
	 
 - Commit your changes and Submit Pull Request to `master` branch of parent project with description and comments
## Testing
Run the knight.py file with requried parameters and arguments that work on your changes.
```
[Inside project root]

python3 knight/knight.py <appropriate args>
``` 


 
