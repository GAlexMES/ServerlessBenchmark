from Tests.IJMeterTest import IJMeterTest
from Tests.T01OverheadTest.OverheadTest import OverheadTest
from Tests.T02ConcurrencyTest.ConcurrencyTest import ConcurrencyTest
from Tests.T03ContainerReuseTest.ContainerReuseTest import ContainerReuseTest
from Tests.T04PayloadTest.PayloadTest import PayloadTest
from Tests.T05OverheadLanguagesTest.OverheadLanguagesTest import OverheadLanguagesTest
from Tests.T06MemoryTest.MemoryTest import MemoryTest
from Tests.T07WeightTest.WeightTest import WeightTest


def get_function_for_number(test_number: str) -> IJMeterTest:
    if test_number == 1:
        return OverheadTest()
    if test_number == 2:
        return ConcurrencyTest()
    if test_number == 3:
        return ContainerReuseTest()
    if test_number == 4:
        return PayloadTest()
    if test_number == 5:
        return OverheadLanguagesTest()
    if test_number == 6:
        return MemoryTest()
    if test_number == 7:
        return WeightTest()

    print("Error! Function with number {0} does not exist!".format(test_number))
