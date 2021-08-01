from treevalue import func_treelize


@func_treelize()
def gcd(a, b):  # GCD calculation
    while True:
        r = a % b
        a, b = b, r
        if r == 0:
            break

    return a


if __name__ == '__main__':
    print("gcd(6, 8):", gcd(6, 8))
    print("gcd(900, 768):", gcd(900, 768))
