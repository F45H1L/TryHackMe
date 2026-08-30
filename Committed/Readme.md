1. Go to the working directory

cd /home/ubuntu/commited

2. List the contents of the directory 

ls -la

3. Inspect the ZIP

unzip -l commited.zip

4. Then extract it

unzip commited.zip

5. Enter the actual repository directory

cd commited

6. Verify

git status

7. See the branches and history

git branch -a

git log --all --oneline --decorate --graph

git log --all --stat

8. List the current directory

ls -la

9. Inspect the current files

cat Readme.md

cat main.py

The suspicious commit is:
c56c470 Oops

10. Inspect the Oops commit

git show c56c470