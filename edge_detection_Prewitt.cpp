/*************************************************************************

edge_detection_Prewitt.cpp | Calculates the "edge content" of 3D brain 
 images given as ASCII files. Called from edgeDetection.py
Please see the user manual for details.

Copyright (C) 2015, Dimitri Perrin

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

************************************************************************/

#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <iterator>
#include <cmath>
#include <cstdlib>

using namespace std;



/**************************************/
/**         printTimestamp()         **/
/**************************************/

/*
 Prints a custom string with the current time and a given message
 Input: the message we want to include
 Output: none
 */

int printTimestamp(string infoString) {
    time_t rawtime;
    struct tm * timeinfo;
    char buffer1 [15];
    
    time (&rawtime);
    timeinfo = localtime (&rawtime);
    strftime (buffer1,80,"%H:%M:%S ->\t",timeinfo);
    
    cout << buffer1 << infoString << endl;
    
    return 0;
}




/********************************/
/**         whichOne()         **/
/********************************/

/*
 Decides which image to use, based on the edge content
 Input: edge content of each image, threshold
 Output: image to use (1: VD, -1: DV, 0: mix)
 */

int whichOne(double VD, double DV, double threshold) {
    double val = (VD-DV)/VD;
    int a=0, b=0;
    if (fabs(val)>threshold)
        a = 1;
    if (val<-threshold)
        b = -2;
    return a+b;
}




/******************************/
/**         access()         **/
/******************************/

/*
 Access a specific position in the array
 Input: array, dimensions, position
 Output: value at this position
 */

double access(double* array, int x, int y, int max_x) {
    return array[y*max_x+x];
}




/********************************/
/**     edgeness_Prewitt()     **/
/********************************/

/*
 Calculates the total edge content using the Prewitt operator
 Input: array, dimensions
 Output: edge content
 */

double edgeness_Prewitt(double* array,int max_x, int max_y) {
    double total = 0.0, centers = 0.0;
    double up, down, left, right, up_left, up_right, down_left, down_right;
    double conv_x, conv_y;
    int x,y;
    for(y=1; y<max_y-1; ++y) {
        for(x=1; x<max_x-1; ++x) {
            centers += access(array,x,y,max_x);
            up = access(array,x,y+1,max_x);
            down = access(array,x,y-1,max_x);
            left = access(array,x-1,y,max_x);
            right = access(array,x+1,y,max_x);
            up_left = access(array,x-1,y+1,max_x);
            up_right = access(array,x+1,y+1,max_x);
            down_left = access(array,x-1,y-1,max_x);
            down_right = access(array,x+1,y-1,max_x);
            conv_x = (up_right+right+down_right)-(up_left+left+down_left);
            conv_y = (up_left+up+up_right)-(down_left+down+down_right);
            total += sqrt(conv_x*conv_x+conv_y*conv_y);
        }
    }
    return total/centers;
}




/********************/
/**     main()     **/
/********************/

int main(int argc, char* argv[]) {
    int hor_size, sag_size, cor_size;
    int i;
    int h, c, s;
    char *DV_ascii, *VD_ascii;
    double **VD_data, **DV_data, **VD_hor_slices, **DV_hor_slices;
    double threshold1=0.05, threshold2=0.1;
    ifstream file_in;
    ofstream file_out;
    string line;
    int *r1, *r2;
    double *VD_edge, *DV_edge;

    
    if(argc!=6) {
        cout << "*** Error. Exactly five arguments are needed.\n";
        return 6;
    }
    
    hor_size = atoi(argv[1]);
    sag_size = atoi(argv[2]);
    cor_size = atoi(argv[3]);
    DV_ascii = argv[4];
    VD_ascii = argv[5];
    
    printTimestamp("Ready to start.");
    
    VD_data = new double*[hor_size*cor_size];
    DV_data = new double*[hor_size*cor_size];
    
    for(i=0;i<hor_size*cor_size;++i) {
        VD_data[i] = new double[sag_size];
        DV_data[i] = new double[sag_size];
    }

    
    /**************************************/
    /**     READING THE ASCII FILES      **/
    /**************************************/
    
    printTimestamp("Starting to read the input files.");

    /* VD */
    
    printTimestamp(VD_ascii);
    
    file_in.open(VD_ascii);
    if (not file_in.is_open()) {
        cout << "*** Error opening VD file.\n";
        return 2;
    }
    
    i=0;
    
    //    cout << "Reading VD." << endl;
    
    /* We read line by line */
    while (getline(file_in,line)) {
        if(line.length()>0) {
            istringstream sin(line);
            double val;
            int nb_values=0;
            while(sin>>val) {
                VD_data[i][nb_values]=val;
                ++nb_values;
            }
            if(nb_values!=sag_size) {
                cout << "Error? size=" << sag_size << ", but " << nb_values << " VD values read.\n";
                return -1;
            }
            ++i;
            
        }
    }
    
    file_in.close();
    
    /* DV */
    
    printTimestamp(DV_ascii);
    
    file_in.open(DV_ascii);
    if (not file_in.is_open()) {
        cout << "*** Error opening DV file.\n";
        return 2;
    }
    
    i=0;
    
    //    cout << "Reading DV." << endl;
    
    /* We read line by line */
    while (getline(file_in,line)) {
        if(line.length()>0) {
            istringstream sin(line);
            double val;
            int nb_values=0;
            while(sin>>val) {
                DV_data[i][nb_values]=val;
                ++nb_values;
            }
            if(nb_values!=sag_size) {
                cout << "Error? size=" << sag_size << ", but " << nb_values << " DV values read.\n";
                return -1;
            }
            ++i;
            
        }
    }
    
    file_in.close();
    
    
    
    /************************************/
    /**     PROCESSING THE FILES      **/
    /************************************/
    
    printTimestamp("Starting to process horizontal slices for both files.");
    
    VD_hor_slices = new double*[hor_size];
    DV_hor_slices = new double*[hor_size];

    r1 = new int[hor_size];
    r2 = new int[hor_size];
    VD_edge = new double[hor_size];
    DV_edge = new double[hor_size];
   
    
    for(h=0; h<hor_size; ++h) {
        VD_hor_slices[h] = new double[sag_size*cor_size];
        DV_hor_slices[h] = new double[sag_size*cor_size];
    }

    
    for(h=0; h<hor_size; ++h) {
        for(c=0; c<cor_size; ++c) {
            for(s=0; s<sag_size; ++s) {
                VD_hor_slices[h][c*sag_size+s] = VD_data[h*cor_size+c][s];
                DV_hor_slices[h][c*sag_size+s] = DV_data[h*cor_size+c][s];
            }
        }
        
        VD_edge[h] = edgeness_Prewitt(VD_hor_slices[h],sag_size,cor_size);
        DV_edge[h] = edgeness_Prewitt(DV_hor_slices[h],sag_size,cor_size);
        
        r1[h] = whichOne(VD_edge[h],DV_edge[h],threshold1);
        r2[h] = whichOne(VD_edge[h],DV_edge[h],threshold2);
    }
    
    
    printTimestamp("Results: ");
    
    cout << "\nSlice\tVD\t\tDV\t" << threshold1 << "\t" << threshold2 << endl;

    for(h=0; h<hor_size; ++h) {

        cout << h << "\t" << VD_edge[h] << "\t" << DV_edge[h] << "\t";

        switch (r1[h]) {
            case -1:
                cout << "DV\t";
                break;
            case 0:
                cout << "mix\t";
                break;
            case 1:
                cout << "VD\t";
                break;
            default:
                cout.precision(8);
                cout << fixed << r1[h] << "\t";
                break;
        }
        switch (r2[h]) {
            case -1:
                cout << "DV\n";
                break;
            case 0:
                cout << "mix\n";
                break;
            case 1:
                cout << "VD\n";
                break;
            default:
                cout.precision(8);
                cout << fixed << r2[h] << "\n";
                break;
        }
    }
    
    printTimestamp("Freeing memory.");

    for(i=hor_size-1; i>=0; --i) {
        delete[] VD_hor_slices[i];
        delete[] DV_hor_slices[i];
    }
    delete[] VD_hor_slices;
    delete[] DV_hor_slices;

    delete[] r1;
    delete[] r2;
    delete[] VD_edge;
    delete[] DV_edge;
    

    for(i=hor_size*cor_size-1; i>=0; --i) {
        delete[] DV_data[i];
        delete[] VD_data[i];
    }
    delete[] DV_data;
    delete[] VD_data;

    printTimestamp("Done.");
    return 0;
}
