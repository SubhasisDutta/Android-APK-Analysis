/**
 * 
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingDeque;

import org.apache.log4j.Logger;

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
    
 * @author fisheye
 *
 */
public class DevicePool {
	
	static Logger logger = Logger.getLogger(DevicePool.class);
	static boolean logDebug = logger.isDebugEnabled();
	
	private BlockingQueue<IDevice> deviceQueue = new LinkedBlockingDeque<IDevice>();
	private Set<IDevice> removedDevices = Collections.synchronizedSet(new HashSet<IDevice>());
	
	private static DevicePool devicePool = new DevicePool();
	
	/**
	 * static constructor for singleton access
	 * @return
	 */
	public static DevicePool getinstance(){
		return devicePool;
	}
	
	/**
	 * @param device
	 */
	public void removeDeviceFromPool(IDevice device){
		removedDevices.add(device);
	}
	
	public void addDeviceToPool(IDevice device){
		if(!deviceQueue.contains(device)){
			deviceQueue.add(device);
		}
	}
	
	public IDevice getDeviceFromPool() throws Exception{
		return deviceQueue.take();
	}
	
	public void returnDeviceToPool(IDevice device){
		//add if online and not present in removed devices set
		if(removedDevices.contains(device)){
			removedDevices.remove(device);
		}else if(device.isOnline()){
			deviceQueue.add(device);
		}
	}
}
