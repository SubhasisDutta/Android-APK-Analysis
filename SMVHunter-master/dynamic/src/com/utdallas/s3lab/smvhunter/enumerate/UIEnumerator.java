/**
 *
 */
package com.utdallas.s3lab.smvhunter.enumerate;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;
import org.eclipse.swt.graphics.Point;

import com.android.chimpchat.hierarchyviewer.HierarchyViewer;
import com.android.ddmlib.IDevice;
import com.android.hierarchyviewerlib.HierarchyViewerDirector;
import com.android.hierarchyviewerlib.device.DeviceBridge;
import com.android.hierarchyviewerlib.device.ViewNode;
import com.android.hierarchyviewerlib.device.ViewNode.Property;
import com.android.hierarchyviewerlib.device.Window;
import com.utdallas.s3lab.smvhunter.monkey.MonkeyMe;
import com.utdallas.s3lab.smvhunter.monkey.NetworkMonitor;

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
public class UIEnumerator extends HierarchyViewerDirector{

	//init logger
	static{
		try {
			PropertyConfigurator.configure("log4j.properties");
		} catch (Exception e) {
			System.out.println("Error configuring Log4j "+ e.getMessage());
		}
	}

	private Executor executor = null;
	public static String screenX;
	public static String screenY;
	private static int initialWindowLength;
	static Logger logger = Logger.getLogger(UIEnumerator.class);
	static boolean logDebug = logger.isDebugEnabled();
	/**
	 *
	 */
	public UIEnumerator(Executor executor) {
		this.executor = executor;
	}

	/**
	 * exec external command
	 * @param command
	 * @return
	 * @throws IOException
	 */
	public static String execCommand(String command) throws IOException{
		logger.info("command executed " + command);
		Process pr = Runtime.getRuntime().exec(command);
		String result = IOUtils.toString(pr.getInputStream());
		pr.destroy();
		return result;
	}

	public static String execSpecial(String command) throws Exception{
		String cmd[] = {
				"/bin/bash",
				"-c",
				command
		};

		logger.info("command executed: "+ command);
		Process pr = Runtime.getRuntime().exec(cmd);

		String result = IOUtils.toString(pr.getInputStream());
		pr.destroy();
		return StringUtils.strip(result);
	}

	private static Set<String> alreadySeen = new HashSet<String>();

	/**
	 * @param eventQueue
	 * @param apkName
	 * @param args
	 * @throws IOException
	 * @throws InterruptedException
	 */
	public static void ListWindows(HierarchyViewer viewer, IDevice device, BlockingQueue<String> eventQueue, String apkName, List<SmartInputBean> smartInput) throws Exception{

		//make the shell device specific
		String emulatorAdb = String.format("%s -s %s shell ", MonkeyMe.adbLocation, device.getSerialNumber());
		if(logDebug) logger.debug(emulatorAdb);

		//get the current window
		Window window = getCurrentWindow(viewer);
		Window windows[] = DeviceBridge.loadWindows(device);
		initialWindowLength = windows.length;

		if(logDebug) logger.debug("intial window length:"+initialWindowLength);

		//check if the current package name is a part of any of the current windows
		boolean appStartError = true;
		String packageName = apkName.split("-")[0];
		for (int i = 0; i < windows.length; i++) {
			Window win = windows[i];
			if(win.getTitle().contains(packageName)){
				appStartError = false;
			}
		}

		//app didnt start. Stuck in the error screen stop here and
		//do double enter
		if(appStartError){
			logger.info(NetworkMonitor.getStringforPrinting("App window title not present in window list", apkName));
			execCommand(String.format("%s input keyevent 66", emulatorAdb));
			execCommand(String.format("%s input keyevent 66", emulatorAdb));
			//stop processing
			return;
		}

		//dump the data to get parent viewnode
		ViewNode node = DeviceBridge.loadWindowData(window);

		//interested lists
		List<ViewNode> clickableNodeList = new ArrayList<ViewNode>();
		List<ViewNode> listviewNodeList = new ArrayList<ViewNode>();
		List<ViewNode> editableNodeList = new ArrayList<ViewNode>();

		//get elements of tree
		traverseTree(node, clickableNodeList, listviewNodeList, editableNodeList);

		//Dont process in case of single webview based apps
		if(editableNodeList.size() == 0 && listviewNodeList.size() == 0 && clickableNodeList.size() == 1 && clickableNodeList.get(0).name.equalsIgnoreCase("android.webkit.WebView")){
			logger.info("App implemented with WebView browser so quitting it");
			return;
		}

		editableNodeList = removeDuplicates(editableNodeList);
		clickableNodeList = removeDuplicates(clickableNodeList);
		listviewNodeList = removeDuplicates(listviewNodeList);

		//implement priority queue
		Collections.sort(clickableNodeList,new ViewNodeComparator());
		Collections.sort(editableNodeList, new ViewNodeComparator());
		Collections.sort(listviewNodeList, new ViewNodeComparator());


		//Automation Start for editable nodes =====================================
		fillEditableNodes(editableNodeList,emulatorAdb, apkName, smartInput);
				
		//for clickable nodes
		for (Iterator<ViewNode> iterator = clickableNodeList.iterator(); iterator.hasNext();) {
			ViewNode viewNode = iterator.next();
			String buttonId = String.format("%s%s", window.getTitle(), viewNode.hashCode);

			Point point = HierarchyViewer.getAbsolutePositionOfView(viewNode);

			//click the button if not already clicked
			if(!alreadySeen.contains(buttonId)){
				
				//check for negative coords and exclude them
				if((point.x >=0 && point.y >= 0 ) && (point.x <= Integer.parseInt(screenX.trim()) && point.y <= Integer.parseInt(screenY.trim()))){

					//click and sleep for a while
					String out = taptap(emulatorAdb, point.x, point.y, apkName, true);
					if(!StringUtils.isEmpty(out)){
						if(logDebug) logger.debug(out);
					}
					alreadySeen.add(buttonId);

					//press back if change in window/focus
					doBackClickonWindowChange(eventQueue, viewer, device, emulatorAdb);

					//check if we have reached the launcher screen
					//if so stop everything and return
					Window currWindow = getCurrentWindow(viewer);
					if(StringUtils.equals(currWindow.getTitle(), "com.android.launcher/com.android.launcher2.Launcher")){
						break;
					}
				}

			}
		}

		//For listview nodes
		if(listviewNodeList != null){
			for (Iterator<ViewNode> iterator = listviewNodeList.iterator(); iterator.hasNext();) {
				ViewNode viewNode = iterator.next();
				String buttonId = String.format("%s%s", window.getTitle(), viewNode.hashCode);

				Point point = HierarchyViewer.getAbsolutePositionOfView(viewNode);
				if(logDebug) logger.debug(String.format("got list view: %s x:%d y:%d", viewNode.name, point.x, point.y));

				//click the button if not already clicked
				if(!alreadySeen.contains(buttonId)){
					if(logDebug) logger.debug(String.format("Listview Node: %s x:%d y:%d", viewNode.name, point.x, point.y));
					//click
					String out = taptap(emulatorAdb, point.x+5, point.y+5, apkName, true);
					if(!StringUtils.isEmpty(out)){
						logger.error(out);
					}
					alreadySeen.add(buttonId);

					//press back if window or focus change
					doBackClickonWindowChange(eventQueue, viewer,device, emulatorAdb);

					//check if we have reached the launcher screen
					//if so stop everything and return
					Window currWindow = getCurrentWindow(viewer);
					if(StringUtils.equals(currWindow.getTitle(), "com.android.launcher/com.android.launcher2.Launcher")){
						break;
					}
				}
			}
		}
	}

	/**
	 * Generate a click event
	 * @param emulator
	 * @param apkName
	 * @param b
	 * @param point
	 * @return
	 * @throws IOException
	 */
	public static synchronized String taptap(String emulator, int x, int y, String apkName, boolean sleep)
			throws IOException {
		if(sleep)
			if(logDebug) logger.debug(NetworkMonitor.getStringforPrinting("before tap log::", System.currentTimeMillis(), apkName, emulator));
		String out = execCommand(String.format("%s input tap %d %d", emulator, x, y));
		try {
			if(sleep){
				Thread.sleep(1000);
			}
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		if(sleep)
			if(logDebug) logger.debug(NetworkMonitor.getStringforPrinting("after tap log::", System.currentTimeMillis(), apkName, emulator));
		return out;
	}

	/**
	 * Get focus at x & y of emulator
	 * @param emulator
	 * @param x
	 * @param y
	 * @param apkName
	 * @param sleep
	 * @return
	 * @throws IOException
	 */
	public static String taptapNonSync(String emulator, int x, int y, String apkName, boolean sleep)
			throws IOException {
		String out = execCommand(String.format("%s input tap %d %d", emulator, x, y));
		if(StringUtils.isNotEmpty(out)){
			logger.error(NetworkMonitor.getStringforPrinting("Input failed",apkName,emulator));
		}
		return out;
	}

	/**
	 * Remove duplicate viewnodes from list
	 * @param nodeList
	 * @return
	 */
	private static List<ViewNode> removeDuplicates(List<ViewNode> nodeList) {
		Map<String, ViewNode> map = new TreeMap<String, ViewNode>();

		for(ViewNode node: nodeList){
			Point pt = HierarchyViewer.getAbsolutePositionOfView(node);
			map.put(String.format("%d%d", pt.x, pt.y), node);
		}

		return new ArrayList<ViewNode>(map.values());
	}

	/**
	 * Populate data into editable nodes
	 * @param editableNodes
	 * @param emulator
	 * @param apkName
	 * @throws IOException
	 */
	private static void fillEditableNodes(List<ViewNode> editableNodes, String emulator, String apkName, List<SmartInputBean> smartInput) throws IOException {
			
		
		//populate editable nodes/elements
		for (Iterator<ViewNode> iterator = editableNodes.iterator(); iterator.hasNext();) {
			ViewNode viewNode = iterator.next();
			
			//get smart inputs for this method
			String inputString = "dummy@gmail.com";
			String idName = viewNode.id;
			for(SmartInputBean siList : smartInput) {
				if(idName.contains(siList.getName())) {
					inputString = getSmartInput(siList);
				}
			}

			Point point = HierarchyViewer.getAbsolutePositionOfView(viewNode);
			
			if(Integer.parseInt(getProperty("text:getSelectionEnd()", viewNode)) == 0 && StringUtils.isEmpty(getStringFromViewNode(viewNode))){
				//get focus on editable item
				String out = taptapNonSync(emulator, point.x, point.y, apkName, false);
				if(!StringUtils.isEmpty(out)){
					logger.error(out);
				}

				//then give input
				//adb shell input <text>
				out = execCommand(String.format("%s input text %s", emulator, inputString));
				if(!StringUtils.isEmpty(out)){
					logger.error(out);
				}
			}
		}
	}
	
	
	private static String getStringFromViewNode(ViewNode node){
		String temp = getProperty("text:mText", node);
		System.out.println(temp);
		return StringUtils.replace(getProperty("text:mText", node), "f)", "");
	}
	
	/**
	 * Get smart inputs
	 * @param smart
	 * @return
	 */
	private static String getSmartInput(SmartInputBean smart) {		
		//check type
		//If its a string
		if(smart.getType().equals("TYPE_CLASS_TEXT")) {
			if(smart.getVariations().equals("TYPE_TEXT_VARIATION_NORMAL")) return "ABCD";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_URI")) return "ftp://dummy.org/dummy.txt";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_EMAIL_ADDRESS")) return "dummy@gmail.com";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_EMAIL_SUBJECT")) return "SMVHunter";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_SHORT_MESSAGE")) return "man in the middle";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_LONG_MESSAGE")) return "man in the middle vulnerability attack";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_PERSON_NAME")) return "Dummy";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_POSTAL_ADDRESS")) return "111 Dummy blvd Dummy 00000";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_PASSWORD")) return "Dummy1234";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_VISIBLE_PASSWORD")) return "Dummy1234";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_WEB_EDIT_TEXT")) return "Dummy Edit Text";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_FILTER")) return "dummy";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_PHONETIC")) return "dummey";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_WEB_EMAIL_ADDRESS")) return "dummy@gmail.com";
			else if(smart.getVariations().equals("TYPE_TEXT_VARIATION_WEB_PASSWORD")) return "Dummy1234";
			else return "XYZ";
		} else if(smart.getType().equals("TYPE_CLASS_NUMBER")) {
			if(smart.getVariations().equals("TYPE_NUMBER_VARIATION_NORMAL")) return "123";
			else if(smart.getVariations().equals("TYPE_NUMBER_VARIATION_PASSWORD")) return "1234";
			else return "12345";
		} else if(smart.getType().equals("TYPE_CLASS_PHONE")) {
			//a 10 digit number
			return "0000000000";
		} else if(smart.getType().equals("TYPE_CLASS_DATETIME")) {
			if(smart.getVariations().equals("TYPE_DATETIME_VARIATION_NORMAL")) return "01011970"; //epoch date
			else if(smart.getVariations().equals("TYPE_DATETIME_VARIATION_DATE")) return "01011970"; //epoch date
			else if(smart.getVariations().equals("TYPE_DATETIME_VARIATION_TIME")) return "000000"; //hr:min:sec
			else return "01011970";
		} else {
			//assume string for null or not-recognized
			return "dummy@gmail.com";
		}
		
	}
	
	/**
	 * Generate a back-click event in case of focus or window change
	 * @param eventQueue
	 * @param viewer
	 * @param device
	 * @param emulator
	 * @throws Exception
	 */
	private static void doBackClickonWindowChange(BlockingQueue<String> eventQueue, HierarchyViewer viewer, IDevice device, String emulator) throws Exception {
		String event = "";
		if((event = eventQueue.poll(5, TimeUnit.SECONDS)) != null){
			Window windows[] = DeviceBridge.loadWindows(device);
			int windowsLength = windows.length;
			if(logDebug) logger.debug("windowsLength after hitting::"+windowsLength+" event:"+event);
			if(StringUtils.equals(WindowUpdate.FOCUS_WINDOW_BOTH_CHANGED, event) || 
					StringUtils.equals(WindowUpdate.FOCUS_CHANGED, event) ||
					StringUtils.equals(WindowUpdate.WINDOW_UPDATED, event)) {
				if(windowsLength > initialWindowLength){
					if(logDebug) logger.debug("Focus + window changed HIT BACK");
					execCommand(String.format("%s input keyevent 4", emulator));
					Thread.sleep(5000);
					Window windows1[] = DeviceBridge.loadWindows(device);

					//this condition will happen when the app didn't respond to back button
					//It might be because of the popup dialog boxes which dont close on back event
					//first enter will focus on it and the second enter will trigger the action
					if(windows1.length > initialWindowLength){
						if(logDebug) logger.debug("App didnt respond to back button...Try ENter");
						execCommand(String.format("%s input keyevent 66", emulator));
						execCommand(String.format("%s input keyevent 66", emulator));

						Window windows2[] = DeviceBridge.loadWindows(device);
						if(windows2.length == initialWindowLength){
							if(logDebug) logger.debug("Hard press succeeded");
						}else{
							if(logDebug) logger.debug("Something going wrong .. need to check it");
						}
					}
					return;
				}
			}
		}
	}

	/**
	 * Get current window that is focussed.
	 * @param viewer
	 * @return
	 */
	private static Window getCurrentWindow(HierarchyViewer viewer) {
		Window currentWindow = viewer.getFocussedWindow();
		if(currentWindow == null){
			//sleep a little n try again..
			try {
				Thread.sleep(5000);
			} catch (InterruptedException e) {
			}
			currentWindow = viewer.getFocussedWindow();
		}
		return currentWindow;
	}

	/**
	 * 
	 * @param node
	 * @param interestedList
	 * @param listViewNodes
	 * @param editableNodes
	 */
	private static void traverseTree(ViewNode node, List<ViewNode> clickableNodeList, List<ViewNode> listViewNodeList, List<ViewNode> editableNodeList){
		
		//populate the editable elements
		if((null != getProperty("text:getSelectionEnd()",node) && Integer.parseInt(getProperty("text:getSelectionEnd()",node)) >= 0)){
			editableNodeList.add(node);
		}
		
		//populate all the clickable elements in the UI
		else if(StringUtils.equals(getProperty("isClickable()", node), "true")){
			clickableNodeList.add(node);
		}

		//workaround for list views where the children are not marked as clickable
		//even though they are.
		if(node.name.equals("android.widget.ListView"))
		{
			for(ViewNode cNode: node.children){
				listViewNodeList.add(cNode);
			}
		}

		for(ViewNode cNode: node.children){
			traverseTree(cNode, clickableNodeList, listViewNodeList, editableNodeList);
		}
	}

	/**
	 * Get node property
	 * @param method
	 * @param node
	 * @return
	 */
	private static String getProperty(String method, ViewNode node){
		Property prop = node.namedProperties.get(method);
		String val = null;
		if(prop != null){
			val = prop.value;
		}
		return val;
	}

	/* (non-Javadoc)
	 * @see com.android.hierarchyviewerlib.HierarchyViewerDirector#getAdbLocation()
	 */
	@Override
	public String getAdbLocation() {
		return MonkeyMe.adbLocation;
	}

	/* (non-Javadoc)
	 * @see com.android.hierarchyviewerlib.HierarchyViewerDirector#executeInBackground(java.lang.String, java.lang.Runnable)
	 */
	@Override
	public void executeInBackground(String taskName, Runnable task) {
		if(logDebug) logger.debug("got task to execute " + taskName);
		executor.execute(task);
	}
}
