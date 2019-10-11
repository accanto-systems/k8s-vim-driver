from k8svimdriver.app import init_app

# The main method below is used when running the application on the command line (either as k8svimdriver or python3 -m k8svimdriver).
# When running in production, with a WSGI server, the create function is used in __init__.py

def main():
    init_app()

if __name__ == '__main__':
    main()
