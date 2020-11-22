import argparse

from .image import create_image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("id")
    args = parser.parse_args()

    create_image(args.id)
