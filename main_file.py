from PyQt5 import QtCore, QtGui, QtWidgets
from qtui import scheduler, list_edit
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree
import xml.dom.minidom
import sys
import datetime

global data
global app
global MainWin
global EditList

pub_filename = 'save_file\publishers.xml'
schedule_filename = 'save_file\schedule.xml'

turn_yellow_after_days = 60
turn_red_after_days = 90


months = ['None', 'January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']
now = datetime.datetime.now()
today = datetime.date(now.year, now.month, now.day)

# This is an extra change to test GitHub

# Define different colors for use.
red = QtGui.QBrush(QtGui.QColor(255, 0, 0))
red.setStyle(QtCore.Qt.NoBrush)
yellow = QtGui.QBrush(QtGui.QColor(200, 200, 0))
yellow.setStyle(QtCore.Qt.NoBrush)
green = QtGui.QBrush(QtGui.QColor(0, 200, 0))
green.setStyle(QtCore.Qt.NoBrush)
blue = QtGui.QBrush(QtGui.QColor(0, 0, 255))
blue.setStyle(QtCore.Qt.NoBrush)
black = QtGui.QBrush(QtGui.QColor(0, 0, 0))
black.setStyle(QtCore.Qt.NoBrush)


class FileManagement(object):
    def __init__(self):
        self.schedule = object
        self.years = object
        self.current_weeks = object
        self.current_year = str(now.year)
        self.sched_load()

        self.root = object
        self.publishers = object
        self.pub_load()

    def sched_load(self):
        self.schedule = ET.parse(schedule_filename)
        self.years = self.schedule.findall('year')
        self.current_weeks_update()

    def sched_save(self):
        self.schedule.write(schedule_filename)
        self.sched_load()

    def talk_save(self, year, week, tag, publisher, council=0):
        found = False
        for y in self.years:
            if y.get('year') == year:
                for w in y.findall('week'):
                    if w.get('week') == week:
                        # if tag == '' or publisher == '':  # In this case, just change the state of 'printed'
                        #     w.set('printed', printed)
                        w.find(tag).set('publisher', publisher)
                        if council != 0:
                            w.find(tag).set('council', council)
                        found = True
                        self.schedule.write(schedule_filename)
                        self.sched_load()
                        break
            if found:
                break

    def current_weeks_update(self):
        for year in self.years:
            if year.get('year') == self.current_year:
                self.current_weeks = year.findall('week')

    def pub_save(self):
        ugly_xml = ET.tostring(self.root)
        fixing = xml.dom.minidom.parseString(ugly_xml)
        pretty_xml = fixing.toprettyxml()
        with open(pub_filename, 'w') as file:
            file.write(pretty_xml)

    def pub_load(self):
        with open(pub_filename, 'r') as file:
            lines = file.readlines()
            newlines = []
            for line in lines:
                newlines.append(line.strip())
            myxml = ''.join(newlines)

        self.root = ET.fromstring(myxml)
        self.publishers = self.root.findall('publishers/publisher')

    def pub_add(self, name):
        publisher = Element('publisher')
        publisher.set('name', name)
        publisher.set('frequency', '1.0')
        lah = Element('last_as_household')
        lah.set('date', '')
        lah.set('prev_date', '')
        publisher.append(lah)
        nc = Element('next_council')
        nc.set('point', '0')
        publisher.append(nc)
        self.root.find('publishers').append(publisher)

        self.pub_save()
        self.pub_load()

    def pub_remove(self, name):
        for pub in self.publishers:
            if pub.get('name') == name:
                self.root.find('publishers').remove(pub)
                self.pub_save()
                self.pub_load()
                break

    def record(self, name, part, date, council):
        if len(part.split()) == 3:  # If part has 3 words, then it is a householder assignment. (First Visit Help)
            for pub in self.publishers:
                if pub.get('name') == name:
                    pub.find('last_as_household').set('prev_date', pub.find('last_as_household').get('date'))
                    pub.find('last_as_household').set('date', date)
                    break
        else:  # Otherwise it is a regular talk assignment.
            talk = Element('talk')
            talk.set('part', part)
            talk.set('council', council)
            talk.set('date', date)
            for pub in self.publishers:
                if pub.get('name') == name:
                    pub.append(talk)
                    break
        self.pub_save()
        self.pub_load()

    def unrecord(self, part, date, name=''):
        if len(part.split()) == 3:  # If part has 3 words, then it is a householder un-assignment. (First Visit Help)
            if name != '':
                for pub in self.publishers:
                    if pub.get('name') == name:
                        pub.find('last_as_household').set('date', pub.find('last_as_household').get('prev_date'))
                        break

        else:  # Otherwise it is a regular talk un-assignment.
            found = False
            for pub in self.publishers:
                talks = pub.findall('talk')
                for talk in talks:
                    if talk.get('date') == date and talk.get('part') == part:
                        # Move the council from the talk being deleted back in as the student's next_council
                        pub.find('next_council').set('point', talk.get('council'))
                        pub.remove(talk)
                        found = True
                        break
                if found:
                    break
        self.pub_save()
        self.pub_load()

    def days_since(self, date_elements, freq=1.0):
        if freq == None:
            freq = 1.0
        else:
            freq = float(freq)
        days = 900
        if type(date_elements) != str:
            for d in date_elements:
                date = str(d.get('date')).split()
                if date == [] or date == ['None']:
                    return days
                month = int(months.index(date[0]))
                day = int(date[1])
                year = int(date[2])
                d1 = datetime.date(year, month, day)
                delta = today - d1
                if delta.days < days:
                    days = delta.days
        else:
            date = date_elements.split()
            month = int(months.index(date[0]))
            day = int(date[1])
            year = int(date[2])
            d1 = datetime.date(year, month, day)
            delta = today - d1
            if delta.days < days:
                days = delta.days
        if days < 0:
            adjusted_time = days * freq
        else:
            adjusted_time = days / freq
        return adjusted_time

    def set_pub_frequency(self, name, freq='1.0'):
        for pub in self.publishers:
            if pub.get('name') == name:
                pub.set('frequency', freq)
                self.pub_save()
                self.pub_load()
                break

    def set_next_council(self, name, council):
        for pub in self.publishers:
            if pub.get('name') == name:
                pub.find('next_council').set('point', council)
                self.pub_save()
                self.pub_load()
                break

    def set_printed_status(self, week, status):
        for w in self.current_weeks:
            if week == w.get('week'):
                w.set('printed', status)
                self.sched_save()
                break

class SchedulerMain(QtWidgets.QMainWindow, scheduler.Ui_MainWindow):
    def __init__(self):
        super(SchedulerMain, self).__init__()
        self.setupUi(self)

        # Variable set in what order the publishers will be sorted.
        # (By last time talk was given or last time as householder)
        self.current_sorting = 'talk'  # Or last_as_household

        # Populate the year_box, and set current to the current year.
        for y in data.years:
            self.year_box.addItem(y.get('year'))

        # When opening the program, set the selected year and week to the current date.
        self.year_box.setCurrentText(str(now.year))
        self.refresh_weeks()
        for i, w in enumerate(data.current_weeks, 0):
            week = w.get('week').split()
            month = int(months.index(week[0]))
            day = int(week[1]) + 3
            if month >= now.month and day >= now.day:
                self.schedule_listbox.setCurrentRow(i)
                self.populate_student_parts()
                break

        self.refresh_publishers()
        self.publisher_listbox.setCurrentRow(0)
        self.populate_pub_stats()

        # Signal connections
        self.btn_close.clicked.connect(self.close)
        self.btn_edit_list.clicked.connect(lambda: EditList.show())
        self.year_box.currentTextChanged.connect(self.refresh_weeks)
        self.schedule_listbox.itemClicked.connect(self.populate_student_parts)
        self.publisher_listbox.itemClicked.connect(self.populate_pub_stats)
        self.rdo_sort_days.clicked.connect(self.change_sorting)
        self.rdo_sort_lah.clicked.connect(self.change_sorting)
        self.freq_box.currentTextChanged.connect(self.set_frequency)
        self.chk_slips_printed.clicked.connect(self.toggle_printed)

        self.assign_reading.clicked.connect(
            lambda: self.assign('reading', 'Reading', self.lbl_read_pub.text()))
        self.assign_fv.clicked.connect(
            lambda: self.assign('first_visit', 'First Visit', self.lbl_fv_pub.text()))
        self.assign_fvh.clicked.connect(
            lambda: self.assign('first_visit_help', 'First Visit Householder', self.lbl_fv_hhold_pub.text()))
        self.assign_rv.clicked.connect(
            lambda: self.assign('return_visit', 'Return Visit', self.lbl_rv_pub.text()))
        self.assign_rvh.clicked.connect(
            lambda: self.assign('return_visit_help', 'Return Visit Householder', self.lbl_rv_hhold_pub.text()))
        self.assign_bs.clicked.connect(
            lambda: self.assign('bible_study', 'Bible Study', self.lbl_bs_pub.text()))
        self.assign_bsh.clicked.connect(
            lambda: self.assign('bible_study_help', 'Bible Study Householder', self.lbl_bs_hhold_pub.text()))

        self.chk_read_cancel.clicked.connect(
            lambda: self.set_cancellation(self.chk_read_cancel, 'reading', 'Reading', self.lbl_read_pub.text()))
        self.chk_fv_cancel.clicked.connect(
            lambda: self.set_cancellation(self.chk_fv_cancel, 'first_visit', 'First Visit', self.lbl_fv_pub.text()))
        self.chk_fvh_cancel.clicked.connect(
            lambda: self.set_cancellation(self.chk_fvh_cancel, 'first_visit_help', 'First Visit Householder', self.lbl_fv_hhold_pub.text()))
        self.chk_rv_cancel.clicked.connect(
            lambda: self.set_cancellation(self.chk_rv_cancel, 'return_visit', 'Return Visit', self.lbl_rv_pub.text()))
        self.chk_rvh_cancel.clicked.connect(
            lambda: self.set_cancellation(self.chk_rvh_cancel, 'return_visit_help', 'Return Visit Householder', self.lbl_rv_hhold_pub.text()))
        self.chk_bs_cancel.clicked.connect(
            lambda: self.set_cancellation(self.chk_bs_cancel, 'bible_study', 'Bible Study', self.lbl_bs_pub.text()))
        self.chk_bsh_cancel.clicked.connect(
            lambda: self.set_cancellation(self.chk_bsh_cancel, 'bible_study_help', 'Bible Study Householder', self.lbl_bs_hhold_pub.text()))

        self.next_council_box.currentTextChanged.connect(self.set_next_council)

    def refresh_weeks(self):
        # Refresh the list of weeks based on the selected year.
        selected = self.schedule_listbox.currentRow()
        data.current_year = self.year_box.currentText()
        data.current_weeks_update()
        self.schedule_listbox.clear()
        for index, week in enumerate(data.current_weeks, 0):
            self.schedule_listbox.addItem(week.get('week'))
            # Color weeks with unassigned parts red.
            if \
               week.find('reading').get('publisher') != '' and \
               week.find('first_visit').get('publisher') != '' and \
               week.find('first_visit_help').get('publisher') != '' and \
               week.find('return_visit').get('publisher') != '' and \
               week.find('return_visit_help').get('publisher') != '' and \
               week.find('bible_study').get('publisher') != '' and \
               week.find('bible_study_help').get('publisher') != '':
                if week.get('printed') == 'True':
                    self.schedule_listbox.item(index).setForeground(black)
                else:
                    self.schedule_listbox.item(index).setForeground(yellow)
            else:
                self.schedule_listbox.item(index).setForeground(red)
        if selected != -1:
            self.schedule_listbox.setCurrentRow(selected)

    def populate_student_parts(self):
        for week in data.current_weeks:
            if week.get('week') == self.schedule_listbox.currentItem().text():
                # Fill in student names and council points
                self.lbl_read_pub.setText(week.find('reading').get('publisher'))
                self.lbl_read_cou.setText(week.find('reading').get('council'))
                self.lbl_fv_pub.setText(week.find('first_visit').get('publisher'))
                self.lbl_fv_cou.setText(week.find('first_visit').get('council'))
                self.lbl_fv_hhold_pub.setText(week.find('first_visit_help').get('publisher'))
                self.lbl_rv_pub.setText(week.find('return_visit').get('publisher'))
                self.lbl_rv_cou.setText(week.find('return_visit').get('council'))
                self.lbl_rv_hhold_pub.setText(week.find('return_visit_help').get('publisher'))
                self.lbl_bs_pub.setText(week.find('bible_study').get('publisher'))
                self.lbl_bs_cou.setText(week.find('bible_study').get('council'))
                self.lbl_bs_hhold_pub.setText(week.find('bible_study_help').get('publisher'))

                # Check for parts that are cancelled and set checkboxes
                self.chk_read_cancel.setChecked(self.lbl_read_pub.text() == 'Cancelled')
                self.chk_fv_cancel.setChecked(self.lbl_fv_pub.text() == 'Cancelled')
                self.chk_fvh_cancel.setChecked(self.lbl_fv_hhold_pub.text() == 'Cancelled')
                self.chk_rv_cancel.setChecked(self.lbl_rv_pub.text() == 'Cancelled')
                self.chk_rvh_cancel.setChecked(self.lbl_rv_hhold_pub.text() == 'Cancelled')
                self.chk_bs_cancel.setChecked(self.lbl_bs_pub.text() == 'Cancelled')
                self.chk_bsh_cancel.setChecked(self.lbl_bs_hhold_pub.text() == 'Cancelled')

                # Check if the slips have been printed and set the checkbox
                self.chk_slips_printed.setChecked(week.get('printed') == 'True')
                break

    def refresh_publishers(self):
        self.publisher_listbox.clear()
        temp_list = []
        for p in data.publishers:
            temp_list.append((p.get('name'), data.days_since(p.findall(self.current_sorting), p.get('frequency'))))

        temp_list.sort(key=lambda tup: tup[1], reverse=True)
        for pub in temp_list:
            self.publisher_listbox.addItem(pub[0])
            # Set font color based on how many days since the last talk
            if pub[1] < 0:
                self.publisher_listbox.item(temp_list.index(pub)).setForeground(blue)
            elif pub[1] < turn_yellow_after_days:
                self.publisher_listbox.item(temp_list.index(pub)).setForeground(green)
            elif pub[1] < turn_red_after_days:
                self.publisher_listbox.item(temp_list.index(pub)).setForeground(yellow)
            else:
                self.publisher_listbox.item(temp_list.index(pub)).setForeground(red)

        self.lbl_total_pubs.setText('Total number of publishers: {}'.format(self.publisher_listbox.count()))

    def change_sorting(self):
        if self.rdo_sort_days.isChecked():
            self.current_sorting = 'talk'
        elif self.rdo_sort_lah.isChecked():
            self.current_sorting = 'last_as_household'
        self.refresh_publishers()
        for i in range(self.publisher_listbox.count()):
            if self.publisher_listbox.item(i).text() == self.lbl_pub_name.text():
                self.publisher_listbox.setCurrentRow(i)

    def populate_pub_stats(self):
        current_pub = object
        try:
            try:
                name = self.publisher_listbox.currentItem().text()
            except AttributeError:
                name = self.lbl_pub_name.text()  # Bug fix: When reassigning the same part to the same publisher,
            for t in data.publishers:            # such as when you just need to update the assigned council point for
                if t.get('name') == name:        # that part, name = self.publisher_listbox... raised AttributeError
                    current_pub = t
                    break

            self.pub_hist_listbox.clear()
            history = []
            for hist in current_pub.findall('talk'):
                sortable = hist.get('date').split()
                sortable = datetime.date(int(sortable[2]), months.index(sortable[0]), int(sortable[1]))
                add_comma_to_date = hist.get('date').split()
                add_comma_to_date = '{} {}, {}'.format(add_comma_to_date[0], add_comma_to_date[1], add_comma_to_date[2])
                history.append((add_comma_to_date, hist.get('part'), hist.get('council'), sortable))
            history.sort(key=lambda tup: tup[3], reverse=True)

        # Compare the list of talk history with the current date to find which have not happened yet, is last, or next.
            last_t = [900, '', '', '0']  # [days_since_last, date, part, council]
            next_t = [-900, '', '', '']
            for h in history:
                self.pub_hist_listbox.addItem('{} - {} ({})'.format(h[0], h[1], h[2]))
                days = (today - h[3]).days
                if days > 0 and days < last_t[0]:
                    last_t[0] = days
                    last_t[1] = h[0]
                    last_t[2] = h[1]
                    last_t[3] = h[2]
                elif days <= 0 and days > next_t[0]:
                    next_t[0] = days
                    next_t[1] = h[0]
                    next_t[2] = h[1]
                    next_t[3] = h[2]
            self.lbl_last_talk.setText(last_t[1])
            self.lbl_last_part.setText(last_t[2])
            self.lbl_last_council.setText(last_t[3])
            self.lbl_next_talk.setText(next_t[1])
            self.lbl_next_part.setText(next_t[2])
            self.lbl_next_council.setText(next_t[3])
            next_council = current_pub.find('next_council').get('point')
            if next_council == '':
                next_council = 0
            else:
                next_council = int(next_council)
            self.next_council_box.setCurrentIndex(next_council)  # (next_t[3]) - 1)
            self.lbl_pub_name.setText(name)
            self.lbl_last_as_household.setText(current_pub.find('last_as_household').get('date'))
            # Convert the saved frequency value to one the user can read and understand.
            freqs = {'0.5': 0, '1': 1, '': 1, None: 1, '1.0': 1, '2': 2, '2.0': 2, '3': 3, '3.0': 3, '4': 4, '4.0': 4}
            self.freq_box.setCurrentIndex(freqs[current_pub.get('frequency')])
        except AttributeError:
            self.lbl_pub_name.setText('New publishers must be added to the list.')

    def assign(self, tag, part, prev_pub):
        # Easy to handle variables
        year = self.year_box.currentText()
        week = self.schedule_listbox.currentItem().text()
        date = '{} {}'.format(week, year)
        name = self.lbl_pub_name.text()
        council = self.next_council_box.currentText()
        data.set_next_council(name, '0')
        # First remove the information from the previous publisher's history
        data.unrecord(part, date, prev_pub)
        # Then save the information into the new publisher's history
        data.record(name, part, date, council)
        # Finally, save the changes into the schedule file
        data.talk_save(year, week, tag, name, council)
        # Then notice that the schedule chances will require a new slip to be printed.
        data.set_printed_status(week, 'False')
        # And refresh the screen
        self.populate_pub_stats()
        self.refresh_publishers()
        self.populate_student_parts()
        self.refresh_weeks()

    def set_next_council(self):
        if self.next_council_box.hasFocus():
            name = self.lbl_pub_name.text()
            council = self.next_council_box.currentText()
            data.set_next_council(name, council)

    def set_frequency(self):
        freq_list = {0: '0.5', 1: '1.0', 2: '2.0', 3: '3.0', 4: '4.0'}
        frequency = freq_list[self.freq_box.currentIndex()]
        name = self.lbl_pub_name.text()
        data.set_pub_frequency(name, frequency)
        self.refresh_publishers()

    def set_cancellation(self, chk_box, tag, part, prev_pub):
        # Easy to handle variables
        year = self.year_box.currentText()
        week = self.schedule_listbox.currentItem().text()
        date = '{} {}'.format(week, year)
        name = 'Cancelled'
        council = '0'
        if chk_box.isChecked():
            # First remove the information from the previous publisher's history
            data.unrecord(part, date, prev_pub)
            # Then save changes to the schedule file
            data.talk_save(year, week, tag, name, council)
        else:
            data.talk_save(year, week, tag, '', council)

        self.populate_pub_stats()
        self.refresh_publishers()
        self.populate_student_parts()
        self.refresh_weeks()

    def toggle_printed(self):
        week = self.schedule_listbox.currentItem().text()
        data.set_printed_status(week, str(self.chk_slips_printed.isChecked()))
        self.refresh_weeks()


class ListEditor(QtWidgets.QWidget, list_edit.Ui_EditPubList):
    def __init__(self):
        super(ListEditor, self).__init__()
        self.setupUi(self)

        self.refresh_publist()

        # Signal connections
        self.pub_list.clicked.connect(self.select)
        self.btn_add.clicked.connect(self.add_pub)
        self.pub_name.returnPressed.connect(self.add_pub)
        self.btn_update.clicked.connect(self.edit_pub)
        self.newname_box.returnPressed.connect(self.edit_pub)
        self.btn_remove.clicked.connect(self.del_pub)
        self.btn_close.clicked.connect(self.done)

    def refresh_publist(self):
        self.pub_list.clear()
        newlist = []
        for p in data.publishers:
            newlist.append(p.get('name'))
        self.pub_list.addItems(sorted(newlist))
        if self.pub_list.count() > 0:
            self.pub_list.setCurrentRow(0)
            self.select()

    def select(self):
        name = self.pub_list.currentItem().text()
        self.pub_name.clear()
        self.lbl_current_name.setText(name)
        self.lbl_del_name.setText(name)

    def add_pub(self):
        if self.pub_name.text() != '':
            name = self.pub_name.text()
            data.pub_add(name)

            self.refresh_publist()
            self.pub_name.clear()

    def edit_pub(self):
        if self.lbl_current_name.text() != '':
            old_name = self.lbl_current_name.text()
            new_name = self.newname_box.text()
            for p in data.publishers:
                if p.get('name') == old_name:
                    p.set('name', new_name)
                    data.pub_save()
                    data.pub_load()
                    self.newname_box.clear()
                    self.refresh_publist()
                    break

    def del_pub(self):
        name = self.pub_list.currentItem().text()
        data.pub_remove(name)

        self.refresh_publist()

    def done(self):
        self.hide()
        MainWin.refresh_publishers()
        if MainWin.publisher_listbox.count() > 0:
            MainWin.publisher_listbox.setCurrentRow(0)
            MainWin.populate_pub_stats()
        else:
            MainWin.lbl_pub_name.setText('New publishers must be added to the list.')


def run():
# if __name__ == "__main__":
    global data
    global app
    global MainWin
    global EditList

    data = FileManagement()
    app = QtWidgets.QApplication(sys.argv)
    MainWin = SchedulerMain()
    EditList = ListEditor()
    MainWin.show()

    sys.exit(app.exec_())


