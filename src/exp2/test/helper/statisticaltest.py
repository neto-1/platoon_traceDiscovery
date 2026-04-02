import numpy as np
import scikit_posthocs as sp


def main():
    data = np.array([[152.9972295, 8.741873979, 16.57702493, 42.73844885],
                     [371.1093266, 30.74380588, 39.56951022, 98.88775277],
                     [687.7729345, 41.29611111, 60.26354742, 218.5414978],
                     [1605.810583, 150.4232092, 225.4561074, 655.8427298],
                     [1668.991843, 183.2881308, 442.2650616, 681.405107],
                     [4111.733897, 805.6953313, 6009.324259, 1835.155955],
                     [7141.467829, 1640.413358, 5810.757015, 2773.24806]])

    # test_result = sp.posthoc_nemenyi_friedman(data) , p_adjust="fdr"
    test_result = sp.posthoc_quade(data, dist="t")

    print(test_result)

    test_result = sp.posthoc_quade(data, dist="t", p_adjust="holm")

    print(test_result)


if __name__ == "__main__":
    main()
