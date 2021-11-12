import sys


class Res_alloc_info:
    index = None
    unit_requested = None


class PCB:
    priority = None
    index = None
    state = None
    parent = None
    children = []
    resources = []

    def create(self, pcbs_list, rl_list, p):
        free = 0
        while True:
            if pcbs[free].state is None:
                break
            else:
                free = free + 1
                if free >= 16:
                    return -1

        pcbs_list[free].state = 1
        self.children.append(free)
        pcbs_list[free].parent = self.index
        pcbs_list[free].priority = p

        rl_list[pcbs_list[free].priority].append(free)

    def request(self, r, k, pcbs_list, rcbs_list, rl_list):
        if rcbs_list[r].state >= k:
            rcbs_list[r].state = rcbs_list[r].state - k
            existing_res = None
            i = 0
            if len(pcbs_list[self.index].resources) > 0:
                for res in pcbs_list[self.index].resources:
                    if res.index == r:
                        existing_res = res
                        break
                    else:
                        i += 1
            if existing_res is not None:
                res_list = pcbs_list[self.index].resources
                res_list[i].unit_requested += k
            else:
                obj = Res_alloc_info()
                obj.index = r
                obj.unit_requested = k
                pcbs_list[self.index].resources.append(obj)
        else:
            self.state = 0  # current process state = blocked
            for i in range(len(rl_list)):
                if self.index in rl_list[i]:
                    rl_list[i].remove(self.index)

            obj = Res_alloc_info()
            obj.index = self.index
            obj.unit_requested = k
            rcbs_list[r].wait_l.append(obj)

    def destroy(self, j, pcbs_list, rcbs_list, rl_list):
        children_index = []
        for child in pcbs_list[j].children:
            children_index.append(child)
        if len(pcbs_list[j].children) > 0:
            for i in range(len(children_index)):
                pcbs_list[j].destroy(children_index[i], pcbs_list, rcbs_list, rl_list)
        if j in self.children:
            self.children.remove(j)
        for i in range(len(rl_list)):
            if j in rl_list[i]:
                rl_list[i].remove(j)
        for i in range(4):
            for blocked_proc in rcbs_list[i].wait_l:
                if blocked_proc.index == j:
                    rcbs_list[i].wait_l.remove(blocked_proc)
        resourcesIndexes = []
        units = []
        for res in pcbs_list[j].resources:
            resourcesIndexes.append(res.index)
            units.append(res.unit_requested)

        for i in range(len(resourcesIndexes)):
            pcbs_list[j].release(resourcesIndexes[i], units[i], pcbs_list, rcbs_list, rl_list)

        pcbs_list[j].state = None
        pcbs_list[j].priority = None
        pcbs_list[j].children.clear()
        pcbs_list[j].resources.clear()

    def release(self, r, k, pcbs_list, rcbs_list, rl_list):
        for res in self.resources:
            if res.index == r and res.unit_requested > k:
                res.unit_requested = res.unit_requested - k
                rcbs_list[r].state = rcbs_list[r].state + k
            elif res.index == r and res.unit_requested == k:
                rcbs_list[r].state = rcbs_list[r].state + k
                # print("In release resource ", res.index)
                self.resources.remove(res)
            else:
                return -1

        while len(rcbs_list[r].wait_l) > 0 and rcbs_list[r].state > 0:
            blocked_proc = rcbs_list[r].wait_l[0]
            if rcbs_list[r].state >= blocked_proc.unit_requested:
                rcbs_list[r].state = rcbs_list[r].state - blocked_proc.unit_requested
                obj = Res_alloc_info()
                obj.index = r
                obj.unit_requested = blocked_proc.unit_requested
                pcbs_list[blocked_proc.index].resources.append(obj)
                pcbs_list[blocked_proc.index].state = 1
                rcbs_list[r].wait_l.remove(blocked_proc)
                rl_list[pcbs_list[blocked_proc.index].priority].append(pcbs_list[blocked_proc.index].index)
            else:
                break

    def timeout(self, rl_list):
        prio = self.priority
        a = rl_list[self.priority].pop(0)
        rl_list[prio].append(a)


class RCB:
    state = None
    inventory = None
    wait_l = []


def init():
    if len(pcbs) > 0:
        for i in range(16):
            if len(pcbs[i].resources) > 0:
                pcbs[i].resources.clear()
            if len(pcbs[i].children) > 0:
                pcbs[i].children.clear()
    pcbs.clear()

    for i in range(16):
        obj = PCB()
        obj.index = i
        obj.state = None
        obj.priority = None
        obj.children = []
        obj.resources = []
        pcbs.append(obj)

    if len(rcbs) > 0:
        for i in range(4):
            if len(rcbs[i].wait_l) > 0:
                rcbs[i].wait_l.clear()
    rcbs.clear()

    for i in range(4):
        obj = RCB()
        if i == 0 or i == 1:
            obj.state = obj.inventory = 1
        elif i == 2:
            obj.state = obj.inventory = 2
        elif i == 3:
            obj.state = obj.inventory = 3
        obj.wait_l = []
        rcbs.append(obj)

    for i in range(3):
        rl[i].clear()

    pcbs[0].priority = 0
    pcbs[0].state = 1
    pcbs[0].parent = None
    rl[0].append(pcbs[0].index)


def scheduler():
    running = None

    for i in range(3, 0, -1):
        i = i - 1
        if len(rl[i]) > 0:
            running = rl[i][0]
            break

    out_file.write(str(running))
    out_file.write(" ")


pcbs = []
rcbs = []
rl = [], [], []  # hold index of pcb
command = None
i = None  # process
r = None  # resource
p = None  # priority
k = None  # units
counter = 0

if len(sys.argv) == 2:
    out_file = open('output.txt', 'w')
    with open(sys.argv[1], 'r') as file:
        lines = file.readlines()

    for line in lines:
        if len(line) > 1:
            a = line.split()
            command = a[0]
            running_proc = None
            for i in range(3, 0, -1):
                i = i - 1
                if len(rl[i]) > 0:
                    running_proc = rl[i][0]
                    break

            if command == "cr":
                p = int(a[1])
                if p == 1 or p == 2:
                    r = pcbs[running_proc].create(pcbs, rl, p)
                    if r == -1:
                        out_file.write("-1")
                        out_file.write(" ")
                    else:
                        scheduler()
                else:
                    out_file.write("-1")
                    out_file.write(" ")
            elif command == "de":
                i = int(a[1])
                # for i in range(4):
                #     for res in pcbs[i].resources:
                #         print(i, res.index, res.unit_requested)
                if 15 >= i > 0 and pcbs[i].state is not None:
                    # print(pcbs[i].state)
                    if running_proc == i:
                        pcbs[running_proc].destroy(i, pcbs, rcbs, rl)
                        scheduler()
                    elif len(pcbs[running_proc].children) > 0:
                        # print(pcbs[i].state)
                        # print(pcbs[running_proc].children)
                        if i in pcbs[running_proc].children:
                            pcbs[running_proc].destroy(i, pcbs, rcbs, rl)
                            scheduler()
                        else:
                            # print("Not children:", i)
                            out_file.write("-1")
                            out_file.write(" ")
                    else:
                        # print("no children in running proc")
                        out_file.write("-1")
                        out_file.write(" ")
                else:
                    # print("Invalid inputs")
                    out_file.write("-1")
                    out_file.write(" ")
            elif command == "rq":
                r = int(a[1])
                k = int(a[2])
                if running_proc == 0:
                    out_file.write("-1")
                    out_file.write(" ")
                elif r == 0 or r == 1:
                    if k == 1:
                        pcbs[running_proc].request(r, k, pcbs, rcbs, rl)
                        scheduler()
                    else:
                        out_file.write("-1")
                        out_file.write(" ")
                elif r == 2:
                    if 2 >= k >= 0:
                        pcbs[running_proc].request(r, k, pcbs, rcbs, rl)
                        scheduler()
                    else:
                        out_file.write("-1")
                        out_file.write(" ")
                elif r == 3:
                    if 3 >= k >= 0:
                        pcbs[running_proc].request(r, k, pcbs, rcbs, rl)
                        scheduler()
                    else:
                        out_file.write("-1")
                        out_file.write(" ")
                else:
                    out_file.write("-1")
                    out_file.write(" ")
            elif command == "rl":
                r = int(a[1])
                k = int(a[2])
                y = False # no resource allocated
                for i in range(4):
                    if i == r:
                        if rcbs[i].state < rcbs[i].inventory:
                            y = True
                if y:
                    if r == 0 or r == 1:
                        if k == 1:
                            result = pcbs[running_proc].release(r, k, pcbs, rcbs, rl)
                            if result == -1:
                                out_file.write("-1")
                                out_file.write(" ")
                            else:
                                scheduler()
                        else:
                            out_file.write("-1")
                            out_file.write(" ")
                    elif r == 2:
                        if 2 >= k >= 0:
                            result = pcbs[running_proc].release(r, k, pcbs, rcbs, rl)
                            if result == -1:
                                out_file.write("-1")
                                out_file.write(" ")
                            else:
                                scheduler()
                        else:
                            out_file.write("-1")
                            out_file.write(" ")
                    elif r == 3:
                        if 3 >= k >= 0:
                            result = pcbs[running_proc].release(r, k, pcbs, rcbs, rl)
                            if result == -1:
                                out_file.write("-1")
                                out_file.write(" ")
                            else:
                                scheduler()
                        else:
                            out_file.write("-1")
                            out_file.write(" ")
                    else:
                        out_file.write("-1")
                        out_file.write(" ")
                else:
                    out_file.write("-1")
                    out_file.write(" ")
            elif command == "to":
                pcbs[running_proc].timeout(rl)
                scheduler()
            elif command == "in":
                if counter == 0:
                    counter += 1
                else:
                    out_file.write("\n")
                init()
                scheduler()
            elif command == "out":
                break
            else:
                out_file.write("-1")
                out_file.write(" ")
    out_file.close()
else:
    print("Can't open file")
