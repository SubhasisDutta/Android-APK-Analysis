/**
 *
 */
package com.utdallas.s3lab.smvhunter.enumerate;

import java.util.concurrent.Executor;


import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import com.android.hierarchyviewerlib.HierarchyViewerDirector;


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
public class WindowUpdate extends HierarchyViewerDirector{
	
	static{
		try {
			PropertyConfigurator.configure("log4j.properties");
		} catch (Exception e) {
			System.out.println("Error configuring Log4j "+ e.getMessage());
		}
	}
	
	static Logger logger = Logger.getLogger(WindowUpdate.class);
	static boolean logDebug = logger.isDebugEnabled();
	
	public static String adbLocation = "";
	private static Executor executors = null;

	public WindowUpdate(Executor executor){
		this.executors = executor;
	}
	
	public static String WINDOW_UPDATED = "WINDOW";
	public static String FOCUS_CHANGED = "FOCUS";
	public static String FOCUS_WINDOW_BOTH_CHANGED = "FOCUS+WINDOW";
	
	@Override
	public String getAdbLocation() {
		return adbLocation;
	}

	@Override
	public void executeInBackground(String taskName, Runnable task) {
		String.format("The task name that is being executed is %s", taskName);
		executors.execute(task);
	}


}
