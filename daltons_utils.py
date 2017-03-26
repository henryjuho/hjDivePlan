# pO2 = fO2 * absolute_pressure


def depth2pressure(dep):
    return dep/10.0 + 1


def pressure2depth(pres):
    return (pres - 1) * 10.0


def mod(o2_mix, po2):
    fo2 = o2_mix/100.0
    depth_press = po2/fo2
    return pressure2depth(depth_press)

# print mod(10)