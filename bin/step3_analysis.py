#!/usr/bin/env python

new_folder = "energies"
old_folder = "energies.old"
write_cutoff = 0.01

def read_confnames():
    confnames = []
    lines = open("head3.lst").readlines()
    for line in lines[1:]:
        fields = line.split()
        if len(fields) < 17:
            continue
        confnames.append(fields[1])
    return confnames

def load_old_backbone():
    backbone_ele = {}
    lines = open("head3.lst").readlines()
    for line in lines[1:]:
        fields = line.split()
        if len(fields) < 17:
            continue
        confid = fields[1]
        epol = float(fields[12])
        backbone_ele[confid] = epol

    return backbone_ele

def load_new_backbone(confnames):
    backbone_ele = {}
    for conf in confnames:
        if conf[:3] == "NTR" or conf[:3] == "CTR" or conf[3:5] == "DM":
            continue    # skip terminal residues as their backbone if off the residue
        fpath = "%s/%s.raw" % (new_folder, conf)
        lines = open(fpath).readlines()
        breakdown = False
        bkb_self = 0.0
        bkb_name = "%sBK%s000" % (conf[:3], conf[5:11])  # find corresponding bkb conformer name
        bkb_inclusive = 0.0
        for line in lines:
            if line[:15] == "[BACKBONE total":
                fields = line.split()
                bkb_inclusive = float(fields[-1])
            if line[:19] == "[BACKBONE breakdown":
                breakdown = True
                continue
            if breakdown:
                fields = line.split()
                if len(fields) > 1 and fields[0] == bkb_name:
                    bkb_self = float(fields[-1])

        bkb_exclusive = bkb_inclusive - bkb_self
        backbone_ele[conf] = (bkb_inclusive, bkb_exclusive)


    return backbone_ele

def load_old_pw(confnames):
    # Will collect those marked with "*" as they have both boundary conditions
    pw = {}
    for conf in confnames:
        if conf[3:5] == "DM":
            continue    # skip dummy
        fname = "%s/%s.opp" % (old_folder, conf)
        lines = open(fname).readlines()
        for line in lines:
            fields = line.strip().split()
            if "*" in fields[-1]:
                single = float(fields[4])
                multi = float(fields[5])
                if abs(single) >= write_cutoff and abs(multi) >= write_cutoff:
                    key = (conf, fields[1])
                    pw[key] = (single, multi)

    return pw


def load_new_pw(confnames):
    # Will collect those marked with "*" as they have both boundary conditions
    pw = {}
    for conf in confnames:
        if conf[3:5] == "DM":
            continue    # skip dummy
        fname = "%s/%s.raw" % (new_folder, conf)
        start = False
        lines = open(fname).readlines()
        for line in lines:
            if line[:9] == "[PAIRWISE":
                start = True
                continue
            elif line[:15] == "[BACKBONE total":
                break
            if start and len(line) > 30:
                fields = line.strip().split()
                
                if fields[-1] == "*":
                    single = float(fields[1])
                    multi = float(fields[2])
                    if abs(single) >= write_cutoff and abs(multi) >= write_cutoff:
                        key = (conf, fields[0])
                        pw[key] = (single, multi)

    return pw


def load_opp(folder, confnames):
    """ Load corrected ele and vdw """
    # Will collect those marked with "*" as they have both boundary conditions
    pw = {}
    for conf in confnames:
        if conf[3:5] == "DM":
            continue    # skip dummy
        fname = "%s/%s.opp" % (folder, conf)
        lines = open(fname).readlines()
        for line in lines:
            fields = line.strip().split()
            ele = float(fields[2])
            vdw = float(fields[3])
            if abs(ele) >= write_cutoff or abs(vdw) >= write_cutoff:
                key = (conf, fields[1])
                pw[key] = (ele, vdw)

    return pw



if __name__ == "__main__":
    confnames = read_confnames()
    old_backbone_ele = load_old_backbone()
    new_backbone_ele = load_new_backbone(confnames)

    # print out bkb comparison
    lines = ["Conformer, Old, New_inc, New_exc\n"]
    for conf in confnames:
        if conf[3:5] == "DM" or conf[:3] == "NTR" or conf[:3] == "CTR":
            continue
        old_ele = 0.0
        new_ele_inc = 0.0
        new_ele_exc = 0.0
        if conf in old_backbone_ele:
            old_ele = old_backbone_ele[conf]
        if conf in new_backbone_ele:
            new_ele_inc, new_ele_exc = new_backbone_ele[conf]
        line = "%s, %8.3f, %8.3f, %8.3f\n" % (conf, old_ele, new_ele_inc, new_ele_exc)
        lines.append(line)
    open("bkb_ele.csv", "w").writelines(lines)

    old_pw = load_old_pw(confnames)
    new_pw = load_new_pw(confnames)
    
    # print pairwise comparison
    lines = ["Conformer1, Conformer2, old_pw_single, new_pw_single, old_pw_multi, new_pw_multi\n"]
    
    for conf1 in confnames:
        if conf1[3:5] == "DM": continue
        for conf2 in confnames:
            if conf2[3:5] == "DM": continue
            if conf1 == conf2: continue
            key = (conf1, conf2)
            old_pw_single = new_pw_single = old_pw_multi = new_pw_multi = 0.0
            found = False
            if key in old_pw:
                old_pw_single, old_pw_multi = old_pw[key]
                found = True
            if key in new_pw:
                new_pw_single, new_pw_multi = new_pw[key]
                found = True

            if found:
                line = "%s, %s, %8.3f, %8.3f, %8.3f, %8.3f\n" % (conf1, conf2, old_pw_single, new_pw_single, old_pw_multi, new_pw_multi)
                lines.append(line)
    
    open("pw_ele.csv", "w").writelines(lines)

    # print pairwise comparison
    lines = ["Conformer1, Conformer2, old_ele, new_ele, old_vdw, new_vdw\n"]

    old_opp_pw = load_opp("../4lzt-old/energies", confnames)
    new_opp_pw = load_opp("energies", confnames)
    #key = ("LYS01A0001_001", "PHE01A0003_001")
    #print(old_opp_pw[key], new_opp_pw[key])
    for conf1 in confnames:
        if conf1[3:5] == "DM": continue
        for conf2 in confnames:
            if conf2[3:5] == "DM": continue
            if conf1 == conf2: continue
            key = (conf1, conf2)
            old_ele = new_ele = old_vdw = new_vdw = 0.0
            found = False
            if key in old_opp_pw:
                old_ele, old_vdw = old_opp_pw[key]
                found = True
            if key in new_opp_pw:
                new_ele, new_vdw = new_opp_pw[key]
                found = True

            if found:
                line = "%s, %s, %8.3f, %8.3f, %8.3f, %8.3f\n" % (
                conf1, conf2, old_ele, new_ele, old_vdw, new_vdw)
                lines.append(line)

    open("pw_opp.csv", "w").writelines(lines)