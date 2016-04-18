/**
 * 
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Queue;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingDeque;
import java.util.zip.CRC32;

import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.collections.Predicate;
import org.apache.commons.collections.Transformer;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import com.android.chimpchat.adb.AdbBackend;
import com.android.chimpchat.hierarchyviewer.HierarchyViewer;
import com.android.ddmlib.AndroidDebugBridge;
import com.android.ddmlib.IDevice;
import com.android.hierarchyviewerlib.device.WindowUpdater;
import com.utdallas.s3lab.smvhunter.enumerate.SmartInputBean;
import com.utdallas.s3lab.smvhunter.enumerate.UIEnumerator;
import com.utdallas.s3lab.smvhunter.enumerate.WindowUpdate;

/**
 * Copyright (C) 2013  David Sounthiraraj

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
 * @author david
 *
 */
public class MonkeyMe implements Runnable{

	static{
		try {
			PropertyConfigurator.configure("log4j.properties");
		} catch (Exception e) {
			System.out.println("Error configuring Log4j "+ e.getMessage());
		}
	}

	static Logger logger = Logger.getLogger(MonkeyMe.class);
	static boolean logDebug = logger.isDebugEnabled();
	static ExecutorService executors;

	private static String ROOT_DIRECTORY ; //location of apps apks
	public static String adbLocation;
	public static Queue<File> apkQueue = null;
	public static Set<String> completedApps = new HashSet<String>();
	public static File completedFile;
	public static String dbLocation; //output of static analysis file
	public static String smartInputLocation; //output of smart input generation
	
	//Files to be used for correlative analysis
	public static String udpDumpLocation; //for UDP dump
	public static String logCatLocation; // for log-cat dump
	public static String straceOutputLocation; //for strace output containing "connect" keyword
	public static String straceDumpLocation; // for all strace output
	
	public static Map<String, List<StaticResultBean>> resultFromStaticAnalysis = new HashMap<String, List<StaticResultBean>>();
	public static Map<String, List<SmartInputBean>> resultFromSmartInputGeneration = new HashMap<String, List<SmartInputBean>>();

	//use a countdown latch to wait till completion
	private static CountDownLatch cdl = new CountDownLatch(1);

	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception{
		
		logger.info("start time ==== " + System.currentTimeMillis());

		try{
			//load the adb location from the props file
			Properties props = new Properties();
			props.load(new FileInputStream(new File("adb.props")));

			//set the adb location
			WindowUpdate.adbLocation = props.getProperty("adb_location");
			adbLocation = props.getProperty("adb_location");
			//set root dir
			ROOT_DIRECTORY = props.getProperty("root_dir");
			//completed txt
			completedFile = new File(ROOT_DIRECTORY+"tested.txt");
			//db location for static analysis
			dbLocation = props.getProperty("db_location");
			//location for smart input generation output
			smartInputLocation = props.getProperty("smart_input_location");
			
			//udp dump location
			udpDumpLocation = props.getProperty("udp_dump_location");
			//logcat dump location
			logCatLocation = props.getProperty("log_cat_location");
			//strace output location
			straceOutputLocation = props.getProperty("strace_output_location");
			//strace dump location
			straceDumpLocation = props.getProperty("strace_output_location");
			
			//set x and y coords
			UIEnumerator.screenX = props.getProperty("x");
			UIEnumerator.screenY = props.getProperty("y");

			DeviceOfflineMonitor.START_EMULATOR = props.getProperty("restart");
			
			//read output of static analysis
			readFromStaticAnalysisText();
			logger.info("Read static analysis output");
			
			readFromSmartInputText();
			logger.info("Read smart input generation output");
			
			

			//populate the queue with apps which are only present in the static analysis
			@SuppressWarnings("unchecked")
			final Set<? extends String> sslApps = new HashSet<String>(CollectionUtils.collect(FileUtils.readLines(new File(dbLocation)), new Transformer() {
				@Override
				public Object transform(Object input) {
					//get app file name
					String temp = StringUtils.substringBefore(input.toString(), " ");
					return StringUtils.substringAfterLast(temp, "/");
				}
			}));
			Collection<File> fileList = FileUtils.listFiles(new File(ROOT_DIRECTORY), new String[]{"apk"}, false);
			CollectionUtils.filter(fileList, new Predicate() {
				@Override
				public boolean evaluate(Object object) {
					return sslApps.contains(StringUtils.substringAfterLast(object.toString(), "/"));
				}
			});
			apkQueue = new LinkedBlockingDeque<File>(fileList);

			logger.info("finished listing files from the root directory");

			try {
				//populate the tested apk list
				completedApps.addAll(FileUtils.readLines(completedFile));
			} catch (Exception e) {
				//pass except
				logger.info("No tested.txt file found");
				
				//create new file
				if(completedFile.createNewFile()) {
					logger.info("tested.txt created in root directory");
				} else {
					logger.info("tested.txt file could not be created");
				}
				
			}
			
			//get the executors for managing the emulators
			executors = Executors.newCachedThreadPool();
			
			//set the devicemonitor exec
			DeviceOfflineMonitor.exec = executors;
			
			final List<Future<?>> futureList = new ArrayList<Future<?>>();


			//start the offline device monitor (emulator management thread)
			logger.info("Starting Device Offline Monitor Thread");
			executors.submit(new DeviceOfflineMonitor());
			
			//get ADB backend object for device change listener
			AdbBackend adb = new AdbBackend();
			
			
			//register for device change and wait for events
			//once event is received, start the MonkeyMe thread
			MonkeyDeviceChangeListener deviceChangeListener = new MonkeyDeviceChangeListener(executors, futureList);
			AndroidDebugBridge.addDeviceChangeListener(deviceChangeListener);
			logger.info("Listening to changes in devices (emulators)");

			//wait for the latch to come down
			//this means that all the apks have been processed
			cdl.await();

			logger.info("Finished testing all apps waiting for threads to join");

			//now wait for every thread to finish
			for(Future<?> future: futureList){
				future.get();
			}



			logger.info("All threads terminated");

			//stop listening for device update
			AndroidDebugBridge.removeDeviceChangeListener(deviceChangeListener);

			//stop the debug bridge
			AndroidDebugBridge.terminate();

			//stop offline device monitor
			DeviceOfflineMonitor.stop = true;

			logger.info("adb and listeners terminated");


		}finally{
			logger.info("Executing this finally");
			executors.shutdownNow();
		}

		logger.info("THE END!!");
	}

	/**
	 * Read static analysis output
	 * @throws IOException 
	 * 
	 */
	private static void readFromStaticAnalysisText() throws IOException {
		Iterator<String> lineIter = FileUtils.lineIterator(new File(dbLocation));
		while (lineIter.hasNext()) {
			String line = lineIter.next();
			String[] info = line.split("[\\s]");
			String apkName = StringUtils.substringAfterLast(info[0], "/");
			String seedName = info[2];
			String seedType = info[3];
			if(resultFromStaticAnalysis.containsKey(apkName)){
				List<StaticResultBean> list = resultFromStaticAnalysis.get(apkName);
				list.add(new StaticResultBean(seedName, seedType));
			}else{
				List<StaticResultBean> list = new ArrayList<StaticResultBean>();
				list.add(new StaticResultBean(seedName, seedType));
				resultFromStaticAnalysis.put(apkName, list);
			}
		}
	}
	
	/**
	 * 
	 * @throws IOException
	 */
	private static void readFromSmartInputText() throws IOException {
		Iterator<String> lineIter = FileUtils.lineIterator(new File(smartInputLocation));
		while (lineIter.hasNext()) {
			String line = lineIter.next();
			String[] info = line.split(";");
			String methName = info[0]; //name of the method
			String inputName = StringUtils.substringAfterLast(info[1], "name: ");
			String inputId = StringUtils.substringAfterLast(info[2], "id: ");
			String inputType = StringUtils.substringAfterLast(info[3], "type: ");
			String inputVar = StringUtils.substringAfterLast(info[4], "variations: ");
			String inputFlag = StringUtils.substringAfterLast(info[5], "flags: ");
			if(resultFromSmartInputGeneration.containsKey(methName)){
				List<SmartInputBean> list = resultFromSmartInputGeneration.get(methName);
				list.add(new SmartInputBean(inputName, inputId, inputType, inputVar, inputFlag));
			}else{
				List<SmartInputBean> list = new ArrayList<SmartInputBean>();
				list.add(new SmartInputBean(inputName, inputId, inputType, inputVar, inputFlag));
				resultFromSmartInputGeneration.put(methName, list);
			}
		}
	}

	/**
	 * Get device name
	 * @param device
	 * @return
	 */
	private String getDeviceString(IDevice device){
		return String.format(adbLocation+" -s %s ", device.getSerialNumber());
	}
	
	/**
	 * Process to execute commands in command line
	 * @param command
	 * @return
	 * @throws IOException
	 */
	public static String execCommand(String command) throws IOException{
		if(logDebug) logger.debug(String.format("Executing command %s", command));
		System.out.println(String.format("Executing command %s", command));
		Process pr = Runtime.getRuntime().exec(command);
		String result = IOUtils.toString(pr.getInputStream());

		pr.destroy();
		return result;
	}
	
	/**
	 * Install app in emulator. This repeats a maximum of two times in case of failure.
	 * @param apkName
	 * @param device
	 * @param packageName
	 * @param count
	 * @throws IOException
	 */
	private void installApk(String apkName, IDevice device, String packageName, int count) throws IOException{
		
		if(count > 2){
			throw new IOException("Install failed too many tries "+ apkName);
		}

		//install the apk 
		String result = execCommand(String.format("%s %s %s", getDeviceString(device), " install ", ROOT_DIRECTORY+apkName));
		if(StringUtils.contains(result, "Failure")){
			logger.error(String.format("%s Install failed for apk  %s with  reason ", device.getSerialNumber(), apkName, result));
			if(!StringUtils.contains(result, "INSTALL_FAILED_ALREADY_EXISTS")){
				throw new IOException("Install failed " + result);
			}else{
				//un-install it and install the same one
				uninstallApk(packageName, device);
				installApk(apkName, device, packageName, count++);
			}
		}
		if(logDebug) logger.debug(String.format("%s Install success for apk  %s", device.getSerialNumber(), apkName));

		try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}


	/**
	 * @param apkName
	 * @return
	 */
	public static String genCrc(String apkName) {
		CRC32 crc = new CRC32();
		crc.update(apkName.getBytes());

		String input = "";
		if(crc.getValue() < 0){
			input = Long.toString(crc.getValue()*-1);
		}else{
			input = Long.toString(crc.getValue());
		}
		return input;
	}


	/**
	 * UI Automation
	 * @param device
	 * @param apkName 
	 */
	private void enumerateCurrentWindow(final IDevice device, String apkName, List<SmartInputBean> smartInput) {
		HierarchyViewer hv = new HierarchyViewer(device);
		
		BlockingQueue<String> eventQueue = new LinkedBlockingDeque<String>();
		MonkeyWindowChangeListener windowListener = new MonkeyWindowChangeListener(eventQueue);
		WindowUpdater.startListenForWindowChanges(windowListener,  device);

		try {
			UIEnumerator.ListWindows(hv, device, eventQueue, apkName, smartInput);
		} catch (Exception e) {
			e.printStackTrace();
		}

		//stop the window updater
		WindowUpdater.stopListenForWindowChanges(windowListener, device);

	}
	
	/**
	 * Uninstall app
	 * @param packageName
	 * @param device
	 * @throws IOException
	 */
	private void uninstallApk(String packageName, IDevice device) throws IOException{
		//uninstall the app
		String result = execCommand(String.format("%s %s %s", getDeviceString(device), " uninstall ", packageName));
		if(StringUtils.contains(result, "Failure")){
			logger.error(String.format("%s uninstall failed for apk  %s", device.getSerialNumber(), packageName));
		}
		if(logDebug) logger.debug(String.format("%s uninstall success for apk  %s", device.getSerialNumber(), packageName));
	}
	
	/**
	 * Add app name to completed file after its execution to prevent test repetition
	 * @param apkName
	 */
	public static synchronized void writeCompleted(String apkName){
		try {
			FileUtils.write(completedFile, apkName+"\n", true);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	//private seen map so that we dont get into an infinite loop
	//we will put the apk back into the yet to be tested pool in case
	//we incur an exception, but we wont test the same app again in this
	//emulator
	private Set<String> seenApks = new HashSet<String>();

	/* (non-Javadoc)
	 * @see java.lang.Runnable#run()
	 * Application Scheduling thread (schedule)
	 */
	@Override
	public void run() {
		if(logDebug) logger.debug("starting thread");
		while(!apkQueue.isEmpty()){
			File apkFile = apkQueue.poll();
			String apkName = apkFile.getName();

			//check if the apk has been tested already
			if(completedApps.contains(apkName) || seenApks.contains(apkName)){
				logger.info(String.format("app %s already tested. Skipping ============", apkName));
				continue;
			}

			//add it to the seen apks
			seenApks.add(apkName);

			IDevice device = null;
			try {

				//get the package name from the apk name
				String[] nameArr = apkName.split("-");
				String packageName = nameArr[0];

				List<StaticResultBean> staticResultBeans = resultFromStaticAnalysis.get(apkName);

				//install only if interested 
				if(staticResultBeans != null && !staticResultBeans.isEmpty()){
					//get a device from pool
					device = DevicePool.getinstance().getDeviceFromPool();

					if(logDebug) logger.debug(String.format("%s installing apk %s", device.getSerialNumber(), apkFile));
					//install the apk
					installApk(apkName, device, packageName, 0);
				}else{ //not interested
					continue;
				}

				logger.info("No of screens to traverse " + staticResultBeans.size());
				
				//start the app and attach strace
				//strace will run for the whole lifetime of the app
				//e.g. start the app  adb shell am start -n ao.bai.https
				execCommand(String.format("%s shell am start -n %s", getDeviceString(device), apkName.replace("-", "/").replace(".apk", "")));
				Future<?> networkFuture = executors.submit(new NetworkMonitor(device, packageName));
				
				//for each vulnerable entry point from static analysis
				for(StaticResultBean resBean : staticResultBeans){
					String seed = resBean.getSeedName();
					String seedType = resBean.getSeedType();
					
					//reset the window before proceeding
					//press enter two times
					execCommand(String.format("%s %s", getDeviceString(device), "shell input keyevent 66"));
					execCommand(String.format("%s %s", getDeviceString(device), "shell input keyevent 66"));

					//seed type can be either activity or service
					//dont process if it is not of the type activity
					if(StringUtils.equalsIgnoreCase(seedType, "activity")){
						//start activity
						//format adb shell am start -n com.ifs.banking.fiid1027/com.banking.activities.ContactUsActivity
						String result = execCommand(String.format("%s %s %s/%s", getDeviceString(device), " shell am start -n ", packageName, seed));
						logger.info("Activity started with result : "+result);
						Thread.sleep(5000);
						
						//get smart input for this method
						List<SmartInputBean> smart = resultFromSmartInputGeneration.get(seed);
						
						//perform UI automation
						enumerateCurrentWindow(device, apkName, smart);
						
					} else if(StringUtils.equalsIgnoreCase(seedType, "service")){
						//ignore
					}else{
						logger.debug(String.format("Did not process seed %s for apk %s ", seed, seedType, apkFile));
					}
				}
				
				//interrupt the network monitor
				networkFuture.cancel(true);
				
				//completed 
				writeCompleted(apkName);

				//uninstall the apk
				uninstallApk(packageName, device);

			} catch (Exception e) {
				logger.error("exception occured " + apkName , e);
				//				apkQueue.add(apkFile);
			}finally{
				//return the device to pool
				if(device != null){
					DevicePool.getinstance().returnDeviceToPool(device);
				}
			}
		}

		//release the latch
		cdl.countDown();
	}
}