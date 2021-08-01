if __name__ == '__main__':
    # map function
    print("Result of map:", list(map(lambda x: x + 1, [2, 3, 5, 7])))

    # filter function
    print("Result of filter:", list(filter(lambda x: x % 4 == 3, [2, 3, 5, 7])))
