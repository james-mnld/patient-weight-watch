# patient-weight-watch

Patient-weight-watch is a live dashboard web-app that allows health practitioners to monitor the weight of cancer patients (and other symptoms they are experiencing) after a radiotherapy treatment. Patients are given a web-form that asks them about their current weight and symptoms information. Upon submission of the form, the information is sent to a database containing all known information about the patient as well as their treatment history. The patient-weight-watch dashboard then fetches the latest patient information for display.

The following information can be found on the main dashboard:
	- Patient ID
	- Lastname
	- Firstname
	- Sex
	- Age
	- Treatment
	- Last Appointment
	- Last Weight
	- Current Weight
	- Change in Weight
	- Last Submission

Upon clicking the RT and symptoms botton on the last column (color-coded according to change in weight) of a specific patient, the following additional information are shown:
	- Symptom levels:
			- Nausea
			- Skin Irritation
			- Difficulty Swallowing
			- Difficulty Breathing
	- Plot of all recorded weights
	- Information for all treatment days:
			- CT images
			- CT images with contours
			- CT images with RT dose
			
TODO:
	- Add warning indicator when one of the symptom levels is greater than a certain threshold
	- Make tables and figures scalable with window size or fixed and scrollable
