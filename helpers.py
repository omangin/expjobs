import sys


def run_class(runnable_class):
    """Function to run target class (for import in script).
    """
    if len(sys.argv) < 3 + 1:
        print 'Invalid arguments. Should be used as:'
        print 'script path_to_config path_to_results name'
        sys.exit(1)
    cfg, path, name = tuple(sys.argv[1:4])
    worker = runnable_class.load_from_serialized(cfg)
    worker.set_out_path_and_name(path, name)
    worker.run()
