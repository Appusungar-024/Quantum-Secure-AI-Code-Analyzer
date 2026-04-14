from validation import run_full_pipeline
from reporter import write_reports


def demo(target='sample_code'):
    report = run_full_pipeline(target)
    paths = write_reports(report)
    print('Reports written:', paths)


if __name__ == '__main__':
    demo()
