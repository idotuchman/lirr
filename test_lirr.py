import unittest, lirr

class DeparturesTestCase(unittest.TestCase):
    def testPageTitle(self):
        title=lirr.getDepartures(11, 8)
        self.failUnless(title=='MTA LIRR - Departing Schedules', 'Returned LIRR webpage title failed')

if __name__ == '__main__': unittest.main()
