

![enter image description here](https://github.com/bradley101/knight/raw/master/knight.jpg)

![Downloads](https://static.pepy.tech/personalized-badge/knight?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)

Knight is a command line utility for doing basic CodeChef operations like problem submission, history, etc directly from the terminal. Trust me it helps 😀
# Parameters & Usage

    usage: knight [-h] [-n] [-l] [--select-contest contest_code] [--reset-contest] [-s problem_code solution_location] [--history problem_code] [-u] [--config] [--logout]

 - `-h or --help` - Displays the standard help on usage and parameters
 - `-n or --nologin` - Performs certain operations that don't require you to log in (currently only `-l or --list-contests`)
 - `--select-contest <contest_code>` - Change the contest to the current ongoing `contest_code`
 - `--reset-contest` - Change the contest to PRACTISE mode
 - `-s <problem code> <solution file> or  --submit <problem code> <solution file>` - Submit your solution file to the specified problem code. **Change the contest to submit to an ongoing contest**.
 - `--history <problem code>` - Display your submission history for that problem in a prettier tabular format. **Change the contest to submit to an ongoing contest**
 - `-u or --user` - Display the currently configured user on **Knight**.
 - `--config` - Set another username and password for logging into Codechef.
 - `--logout` - Logs out the configured user on Codechef (if logged in)

Note: **Knight** uses sessions  so your previous login session is saved for later use.

## Usage Examples

 - For **ONGOING** contest, If you want to select contest JUN20 (Div 2), just go to the Div 2 contest page and copy the last part of the URL. So it'll be JUN20B.

	 `knight --select-contest JUN20B`

	After this you can submit solutions to the problem inside the contest page by the following command

	`knight -s <problem_code> <solution_file_location>`

 - For **PAST** contests or **PRACTISE** problems, reset the contest if you haven't already done by `knight --reset-contest`
 
	 Then just do `knight -s <problem_code> <solution_file_location>`
Example - `knight -s COVDSMPL src/COVDSMPL.cpp`

 - For an **ONGOING** contest you must set the `--select-conetest` parameter once

# Installation

`$ pip install knight --upgrade`

 
You need to add installation directory to `PATH`. At the end of the installation, you'll be notified by a warning with a location/directory. Copy that location and add it to system's `PATH` variable.
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


 
