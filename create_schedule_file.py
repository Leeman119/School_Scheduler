import calendar
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree
import xml.dom.minidom

cal = calendar.Calendar()

filename = 'schedule.xml'
start_year = 2017
end_year = 2050

# Loop creating the xml file of the weekly schedule for the chosen years.
years = Element('years')
sched_tree = ElementTree(years)
for y in range(start_year, end_year + 1):
    year = Element('year')
    year.set('year', str(y))
    years.append(year)

    for m in range(1, 13):
        print(calendar.month_name[m])
        first_of_month = True
        weeks = cal.monthdayscalendar(y, m)

        for w in weeks:
            if w[0] != 0:
                print("Monday the " + str(w[0]))
                week = Element('week')
                week.set('week', '{} {}'.format(calendar.month_name[m], str(w[0])))
                week.set('printed', 'False')

                read = Element('reading')
                week.append(read)
                read.set('publisher', '')
                read.set('council', '0')

                first_visit = Element('first_visit')
                week.append(first_visit)
                first_visit.set('publisher', '')
                first_visit.set('council', '0')

                fvhelp = Element('first_visit_help')
                week.append(fvhelp)
                fvhelp.set('publisher', '')

                return_visit = Element('return_visit')
                week.append(return_visit)
                return_visit.set('publisher', '')
                return_visit.set('council', '0')

                rvhelp = Element('return_visit_help')
                week.append(rvhelp)
                rvhelp.set('publisher', '')

                bible_study = Element('bible_study')
                week.append(bible_study)
                bible_study.set('publisher', '')
                bible_study.set('council', '0')

                bshelp = Element('bible_study_help')
                week.append(bshelp)
                bshelp.set('publisher', '')

                if first_of_month:
                    first_visit.set('publisher', 'Cancelled')
                    fvhelp.set('publisher', 'Cancelled')
                    return_visit.set('publisher', 'Cancelled')
                    rvhelp.set('publisher', 'Cancelled')
                    bible_study.set('publisher', 'Cancelled')
                    bshelp.set('publisher', 'Cancelled')
                    first_of_month = False

                year.append(week)
ugly_xml = ET.tostring(years)
xml = xml.dom.minidom.parseString(ugly_xml)
pretty_xml = xml.toprettyxml()


with open(filename, 'w') as file:
    file.write(pretty_xml)

