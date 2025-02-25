
from electrical_source import *

def main():
    electricalSource = ElectricalSource()
    powerSet = 12.2
    powerCom = 'COM66'

    electricalSource.open(powerSet, 1, powerCom)

    readInterval = 0.1
    electricalSource.open(powerSet, 1, powerCom)
    lastCurErr = time.time()
    average = 0
    cntAll = 0
    currentAll = 0
    currentMax = 0
    start = time.time()
    while True:
        current = electricalSource.get_current()
        if current > currentMax:
            currentMax = current
        cntAll = cntAll + 1
        currentAll = currentAll + current
        average = currentAll / cntAll


        print (time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(current)[:5].rjust(3, ' '), str(average)[:5].rjust(3, ' '), '  ==========  ', (time.time() - start) / 60)

        time.sleep(readInterval)

if __name__ == '__main__':
    main()
