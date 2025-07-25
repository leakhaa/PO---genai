


I want to develop a automated system using genai for automating a task in warehouse management system.
  use case : The main working of the task is like  User will report for missing po/asn/pallet/quantity mismatch. 
  ASN - 5 digit number starts with 0
  PO -  10 digit number starts with 2
  PALLET ID - 15 digit number start with 5
  
 An  asn may have multiple po and a single po has multiple pallet with the specific quantity 
 Eg. Po 1 has 4 pallet with each quantities of 2 So po 1 has 8 quantities  Po 2 has 6 pallets with 1 quantity each
 So po 2 has 6 quantities These two PO are mapped to 1 asn. So this asn has total of 14 quantities
 
 db idea :
  there are 4 tables:
  PO header - columns: distinct PO ID, status( inprogress, received, hold) , last updated date (details updated lastly)
  PO line - col: pallet id , their PO, ASN, last update date and time , sum of quantity. (this  may include duplicate PO as one po has many pallets)
  ASN header - list of distinct ASN , last updated date ,supplier referece(eg abc123)
  ASN line - pallet id , po, asn , suplier refernce, last update date , sum of qunatity..
  
  
 scenerios :
   There are four scenerios:
   1. missing ASN - If the issue decription as asn is missing then , then it should check the asn header as well as asn line to check the entry. 
     if asn is present then mail to user saying " the asn is interfaced into the wms successfully " and the snippets of the table with asn highlighted.
	 if not then mail to SAP saying please trigger asn and asn id - xxxx.
	 wait for the response and after triggering check once if it is interfaced into the table. and mail to user saying the issue is resolved .
	 
   2. missing PO - if the issue description is as the po is missing then it should check the all po header and line and asn line tables for the entry 
    if yes  check if the number pallet and sum of qty is same in asn line and po line .
	if all are correct then mail to user saying " the po is interfaced into the wms successfully and the snippets of the table with records highlighted.
	if not , 
	if po is missing , mail to SAP saying that triger PO  and PO id .
	wait for their response and check with the db if it has been interfaced into the system. if the issue is resolved mail to the user saying that the issue has been resolved.
	if the pallet count is not same - follow the steps in the qunatity mismatch scenario.
	if the pallet is missing then follow steps in scenerio step 3.
	
   3. missing pallet - if the issue description is as the pallet is missing for specific po/asn. then it should check in po line and asn line if the pallet is missing. 
      If the pallet is present sent the mail to user saying that the issue has been resolved .
	  if not mail to SAP saying , gives the pallet asn and po deatils for whatever data given (eg po and asn)
	  wait for the response , now read the excel sheet in the mail. check if all tha pallets is matching in excel and db.
	  if pallet are missing write a script to add the deatils from the excel into the po line and asn line table.
	  check if it is interfaced successfully . then mail to user saying that the issue got resolved and interfaced successfully including snippets of both excel and db ( highlight the matching sum of qty in excel and db)
	  
   4. if the issue is as mismtach quantity - then read the if the po/pallet/asn is given . mail to SAP saying to provide the details for the parameter given.
    wait for the response  then read the file and match with db follow all the steps above to check if the asn is missing or the po is missing or pallet is missing.
	take necessary action according to it. check if all the details are interfaced. mail to user saying the issue has been resolved.
	
	these are the scenerios that has to be implemented.
	
	 now write a full code for this system using ai llm model which are free and open source. also give decription about what technologies are used.
	 also prepare a synthetic data for the tables using faker.
	 
 
