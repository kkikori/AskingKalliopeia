from collections import OrderedDict


def main():
    nums = OrderedDict()
    nums[1] = "one"
    nums[2] = "two"
    nums[3] = "three"
    print(nums.keys())
    print(next(reversed(nums)))


if __name__ == '__main__':
    main()
