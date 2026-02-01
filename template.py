template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QWidget" name="formLayoutWidget">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>20</y>
      <width>229</width>
      <height>121</height>
     </rect>
    </property>
    <layout class="QFormLayout" name="layout">
     <item row="0" column="0">
      <widget class="QLabel" name="first_person_label">
       <property name="text">
        <string>Первый Актёр</string>
       </property>
      </widget>
     </item>
     <item row="0" column="1">
      <widget class="QLineEdit" name="first_person"/>
     </item>
     <item row="1" column="0">
      <widget class="QLabel" name="second_person_label">
       <property name="text">
        <string>Второй Актёр</string>
       </property>
      </widget>
     </item>
     <item row="1" column="1">
      <widget class="QLineEdit" name="second_person"/>
     </item>
     <item row="2" column="0" colspan="2">
      <widget class="QPushButton" name="submit_button">
       <property name="text">
        <string>Найти</string>
       </property>
      </widget>
     </item>
     <item row="3" column="0" colspan="2">
      <widget class="QLabel" name="error_bar">
       <property name="text">
        <string/>
       </property>
      </widget>
     </item>
    </layout>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>26</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>"""