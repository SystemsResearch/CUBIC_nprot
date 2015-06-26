/*************************************************************************
 
 file_merging.cpp | Merges two 3D brain images given as ASCII files based
 on the threshold values calculated during "edge detection".
 Called from fileMerging.py
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

#define BUFFER_SIZE 10000

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
/**         factor_DV()        **/
/********************************/

/*
 Calculates the weight for the DV image
 Input: position, size, n/m thresholds
 Output: weight
 */

double factor_DV(int position, int n, int m) {
    double weight;
    if(position<=n) {
        weight=0.0;
    }
    else {
        if(position>=m) {
            weight=1.0;
        }
        else {
            double a,b;
            a = 1.0 / (m-n);
            b = ((float)n) / (n-m);
            weight = a*position + b;
        }
    }
    return weight;
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




/********************/
/**     main()     **/
/********************/

int main(int argc, char* argv[]) {
    int hor_size, sag_size, cor_size;
    int i, j;
    int h, c, s;
    int n,m;
    char *DV_ascii, *VD_ascii, *out_ascii;
    double **VD_data, **DV_data, **merged_data;
    double DV_value, VD_value, factor;
    ifstream file_in;
    ofstream file_out;
    string line;

    
    if(argc!=9) {
        cout << "*** Error. Exactly eight arguments are needed.\n";
        return 9;
    }
    
    hor_size = atoi(argv[1]);
    sag_size = atoi(argv[2]);
    cor_size = atoi(argv[3]);
    DV_ascii = argv[4];
    VD_ascii = argv[5];
    out_ascii = argv[6];
    n = atoi(argv[7]);
    m = atoi(argv[8]);
    
    printTimestamp("Ready to start.");
    
    VD_data = new double*[hor_size*cor_size];
    DV_data = new double*[hor_size*cor_size];
    merged_data = new double*[hor_size*cor_size];
    
    for(i=0;i<hor_size*cor_size;++i) {
        VD_data[i] = new double[sag_size];
        DV_data[i] = new double[sag_size];
        merged_data[i] = new double[sag_size];
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
    
    printTimestamp("Starting to combine the horizontal slices.");
    
    
    for(h=0; h<hor_size; ++h) {
        
        for(c=0; c<cor_size; ++c) {
            for(s=0; s<sag_size; ++s) {
                VD_value = VD_data[h*cor_size+c][s];
                DV_value = DV_data[h*cor_size+c][s];
                factor = factor_DV(h,n,m);
                merged_data[h*cor_size+c][s] = factor*DV_value + (1-factor)*VD_value;
            }
        }
        
    }
    
    
    printTimestamp("Saving the results.");

    file_out.open(out_ascii);
    if (not file_out.is_open()) {
        cout << "*** Error opening output file.\n";
        return 3;
    }
    
    for(i=0; i<hor_size*cor_size; ++i) {
        for(j=0; j<sag_size; ++j) {
            int val = (int)merged_data[i][j];
            file_out << val << " ";
        }
        file_out << endl;
    }
    file_out << endl;

    
    printTimestamp("Freeing memory.");

    
    for(i=hor_size*cor_size-1; i>=0; --i) {
        delete[] DV_data[i];
        delete[] VD_data[i];
        delete[] merged_data[i];
    }
    delete[] DV_data;
    delete[] VD_data;
    delete[] merged_data;
    
    printTimestamp("Done.");
    return 0;
}
