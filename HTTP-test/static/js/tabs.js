let stateNumber = 1;

function openGraph(evt, patientName) {
    var i, tablinks;
  
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(patientName).style.display = "block";
    evt.currentTarget.className += " active";
  }

  function deleted (){//evt, cityName) {
    var i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  }

function patientSelectedWrapper(evt, patientName, patientName1, patientName2, patientName3, patientName4, patientNumber) {
    deleted();//evt, patientName);
    openGraph(evt, patientName);
    openGraph(evt, patientName1);
    openGraph(evt, patientName2);
    openGraph(evt, patientName3);
    openGraph(evt, patientName4);
    stateNumber = patientNumber;
}

function patientRealTime(evt, patientName, patientName1, patientName2) {
  deleted();
  openGraph(evt, patientName)
  openGraph(evt, patientName1);
  openGraph(evt, patientName2);
}

function startGiveState(patientNumber) {
  stateNumber = patientNumber;
}