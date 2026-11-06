"""
Example Helper Script for Custom Skill
"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Skill Helper Utility")
    parser.add_argument("--input", "-i", type=str, help="Path to input file")
    args = parser.parse_args()
    print("Example skill helper running with input:", args.input)

if __name__ == '__main__':
    main()
