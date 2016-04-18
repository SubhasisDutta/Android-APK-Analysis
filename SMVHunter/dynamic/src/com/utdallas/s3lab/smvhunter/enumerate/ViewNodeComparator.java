package com.utdallas.s3lab.smvhunter.enumerate;

import java.util.Comparator;

import org.eclipse.swt.graphics.Point;

import com.android.chimpchat.hierarchyviewer.HierarchyViewer;
import com.android.hierarchyviewerlib.device.ViewNode;

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
public class ViewNodeComparator implements Comparator<ViewNode>{

	@Override
	public int compare(ViewNode o1, ViewNode o2) {
		Point op1 = HierarchyViewer.getAbsolutePositionOfView(o1);
		Point op2 = HierarchyViewer.getAbsoluteCenterOfView(o2);
		if(op1.y < op2.y){
			return -1;
		}else if(op1.y > op2.y){
			return 1;
		}else{
			return 0;
		}

	}

}
