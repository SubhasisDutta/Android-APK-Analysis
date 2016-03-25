/**
 * 
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.util.HashSet;
import java.util.Iterator;
import java.util.concurrent.BlockingQueue;

import org.apache.log4j.Logger;

import com.android.ddmlib.IDevice;
import com.android.hierarchyviewerlib.device.WindowUpdater.IWindowChangeListener;
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

public class MonkeyWindowChangeListener implements IWindowChangeListener,Runnable {

	static Logger logger = Logger.getLogger(MonkeyWindowChangeListener.class);
	static boolean logDebug = logger.isDebugEnabled();

	private BlockingQueue<String> eventQueue;
	public static HashSet<String> eventsSet = new HashSet<String>();
	
	/**
	 * @param eventQueue
	 */
	public MonkeyWindowChangeListener(BlockingQueue<String> eventQueue) {
		this.eventQueue = eventQueue;
		Thread eventsThread = new Thread(this);
		eventsThread.start();
	}



	/* (non-Javadoc)
	 * @see com.android.hierarchyviewerlib.device.WindowUpdater.IWindowChangeListener#windowsChanged(com.android.ddmlib.IDevice)
	 */
	@Override
	public void windowsChanged(IDevice device) {
		eventsSet.add(WindowUpdate.WINDOW_UPDATED);
		if(logDebug) logger.debug("window changed here:"+WindowUpdate.WINDOW_UPDATED);
	}

	/* (non-Javadoc)
	 * @see com.android.hierarchyviewerlib.device.WindowUpdater.IWindowChangeListener#focusChanged(com.android.ddmlib.IDevice)
	 */
	@Override
	public void focusChanged(IDevice device) {
		//eventQueue.add(WindowUpdate.FOCUS_CHANGED);
		if(logDebug) logger.debug("Focus changed here:"+WindowUpdate.FOCUS_CHANGED);	
		eventsSet.add(WindowUpdate.FOCUS_CHANGED);
	}

	@Override
	public void run() {
		while(true){

			try {
				Thread.sleep(2000);
			} catch (InterruptedException e) {
				e.printStackTrace();
				return;
			}
			
			synchronized(eventsSet){
				try {
					Iterator<String> eventIterator = eventsSet.iterator();
					String caughtEvent = null;
					boolean isFocusChanged= false;
					boolean isWindowChanged = false;
					while(eventIterator.hasNext()){
						caughtEvent = eventIterator.next();
						if(caughtEvent.equalsIgnoreCase(WindowUpdate.FOCUS_CHANGED)){
							isFocusChanged = true;
						}
						else if(caughtEvent.equalsIgnoreCase(WindowUpdate.WINDOW_UPDATED)){
							isWindowChanged = true;
						}
					}
					
					if(isFocusChanged && isWindowChanged){
						eventQueue.add(WindowUpdate.FOCUS_WINDOW_BOTH_CHANGED);
					}
					else if(isWindowChanged){
						eventQueue.add(WindowUpdate.WINDOW_UPDATED);
					}
					else if(isFocusChanged){
						eventQueue.add(WindowUpdate.FOCUS_CHANGED);
					}
					
					//clear the temporary event cache
					eventsSet.clear();
					
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		}
	}

}
