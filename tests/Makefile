all: bin/stdin_target bin/stdin_target bin/wordle

bin/stdin_target: targets/target.c
	gcc targets/target.c -g -DSTDIN_INPUT -o bin/stdin_target

bin/file_target: targets/target.c
	gcc targets/target.c -g -DFILE_INPUT -o bin/file_target

bin/wordle: targets/wordle.c
	gcc targets/wordle.c -g -o bin/wordle
