from invoke import task

LINE_LENGTH = "90"

PATHS = ["dook", "tests"]
EXCLUDE = ["*/migrations/*"]


@task
def isort(c):
    options = [
        "--recursive",
        "--multi-line=3",
        "--trailing-comma",
        "--force-grid-wrap=0",
        "--use-parentheses",
        "--atomic",
        f"--line-width={LINE_LENGTH}",
        '-sg="*/migrations/*"'
    ]
    c.run(f"isort {' '.join(PATHS)} {' '.join(options)}")


@task
def black(c):
    options = [f"--line-length={LINE_LENGTH}", f"--exclude=.*/migrations/*"]
    c.run(f"black {' '.join(PATHS)} {' '.join(options)}")


@task 
def autoflake(c):
    options = ["--in-place --remove-all-unused-imports --remove-unused-variables"]
    c.run(f"find . -name '*.py'|grep -v migrations|xargs autoflake {' '.join(options)}")


@task
def reformat(c):
    isort(c)
    black(c)
    autoflake(c)
