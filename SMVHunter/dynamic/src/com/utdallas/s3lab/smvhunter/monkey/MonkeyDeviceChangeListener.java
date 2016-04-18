/**
 * 
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;

import org.apache.log4j.Logger;

import com.android.ddmlib.AndroidDebugBridge.IDeviceChangeListener;
import com.android.ddmlib.IDevice;

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
public class MonkeyDeviceChangeListener implements IDeviceChangeListener{

	private ExecutorService executors;
	private List<Future<?>> futureList;
	static Logger logger = Logger.getLogger(MonkeyDeviceChangeListener.class);
	static boolean logDebug = logger.isDebugEnabled();
	private static Set<String> managedDevices = Collections.synchronizedSet(new HashSet<String>());
	

	/**
	 * @param executors
	 */
	public MonkeyDeviceChangeListener(ExecutorService executors, List<Future<?>> futureList) {
		this.executors = executors;
		this.futureList = futureList;
		
	}

	@Override
	public void deviceDisconnected(IDevice device) {
		DevicePool.getinstance().removeDeviceFromPool(device);
		
		//remove the managed device
		managedDevices.remove(device.getSerialNumber());
	}

	@Override
	public void deviceConnected(final IDevice device) {
		logger.info("device connected " + device.getSerialNumber());
		
		//now add the device to the pool
		DevicePool.getinstance().addDeviceToPool(device);
		
		
		if(!managedDevices.contains(device.getSerialNumber())){
			//create a thread for every device that is connected
			logger.info("Starting testing thread for device "+device.getSerialNumber());
			Future<?> future = executors.submit(new MonkeyMe());
			futureList.add(future);
			
			//start the monitors for the device
			//only one per device
			//capture UDP and Logcat for Correlative Analysis
			executors.submit(new UDPMonitor(device));
			executors.submit(new LogcatMonitor(device));
			
			//add it to the managed devices
			managedDevices.add(device.getSerialNumber());
		}else{
			logger.info("Somebody is already managing the device so ignoring "+ device.getSerialNumber());
		}
		
	}

	@Override
	public void deviceChanged(IDevice device, int changeMask) {
		if ((changeMask & IDevice.CHANGE_STATE) != 0 && device.isOnline()) {
			logger.info("device changed "+ device.getSerialNumber()+" change mask "+ (changeMask & IDevice.CHANGE_STATE));
			deviceConnected(device);
		}
	}
}
