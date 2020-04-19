# Puzzles
 Download Daily Newsday Crossword and Daily Sudoku with Frontend Calendar
 
Puzzles will be saved as:
    BASE-PATH-TO-SAVE-PUZZLES\
                              crosswords\
							              puzzle
									      solution
							  sudoku\
							         puzzle
									 solution
									 

If the puzzle fails to download, it will redirect to live link

Example Docker-Compose File

    puzzles:
        container_name: puzzles
        image: puzzles
        build:
            dockerfile: ./Puzzles/Dockerfile
            context: ./Puzzles
        ports:
            - EXTERNAL-PORT:80
        environment:
            - WEB_ROOT=/
        volumes:
            - BASE-PATH-TO-SAVE-PUZZLES:/app/docs
            - BASE-PATH-TO-LOGS:/app/logs
        restart: unless-stopped