# patient-weight-watch

Patient-weight-watch is a live dashboard web-app that allows health practitioners to monitor the weight of cancer patients (and other symptoms they are experiencing) after a radiotherapy treatment. Patients are given a web-form that asks them about their current weight and symptoms information. Upon submission of the form, the information is sent to a database containing all known information about the patient as well as their treatment history. The patient-weight-watch dashboard then fetches the latest patient information for display.

The following information can be found on the main dashboard:
<ul>
	<li> Patient ID </li>
	<li> Lastname </li>
	<li> Firstname </li>
	<li> Sex </li>
	<li> Age </li>
	<li> Treatment </li>
	<li> Last Appointment </li>
	<li> Last Weight </li>
	<li> Current Weight </li>
	<li> Change in Weight </li>
	<li> Last Submission </li>
</ul>

Upon clicking the RT and symptoms botton on the last column (color-coded according to change in weight) of a specific patient, the following additional information are shown:
<ul>
	<li> Symptom levels: </li>
		<ul>
			<li> Nausea </li>
			<li> Skin Irritation </li>
			<li> Difficulty Swallowing </li>
			<li> Difficulty Breathing </li>
		</ul>
	<li> Plot of all recorded weights </li>
	<li> Information for all treatment days: </li>
		<ul>
			<li> CT images </li>
			<li> CT images with contours </li>
			<li> CT images with RT dose </li>
		</ul>
</ul>
			
TODO:
<ul>
	<li> Error handlers that check the validity of the webform values submitted </li>
	<li> Handlers for web errors </li>
	<li> Add warning indicator when one of the symptom levels is greater than a certain threshold </li>
	<li> Make tables and figures scalable with window size or fixed and scrollable </li>
	<li> Option for user to modify weight thresholds for color coding </li>
</ul>
