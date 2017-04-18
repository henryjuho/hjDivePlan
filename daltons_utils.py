import math

# pO2 = fO2 * absolute_pressure


def depth2pressure(dep):
    return dep/10.0 + 1


def pressure2depth(pres):
    return (pres - 1) * 10.0


def mod(o2_mix, po2):
    fo2 = o2_mix/100.0
    depth_press = po2/fo2
    return pressure2depth(depth_press)


def litres4dive(sac, depth, time):
    ltrs4dive = sac * time
    dep_press = depth2pressure(depth)
    ltrs_at_depth = ltrs4dive * dep_press
    return ltrs_at_depth


def cyl_reqs(volume, cyl_size):
    max_op_pres = 232.0
    max_vol = max_op_pres * cyl_size
    no_cyls = math.ceil(volume / max_vol)
    per_cyl_v = volume / no_cyls
    per_cyl_bar = per_cyl_v / cyl_size
    return no_cyls, per_cyl_bar
