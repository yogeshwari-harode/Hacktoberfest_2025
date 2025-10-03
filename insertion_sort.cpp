#include<iostream>
#define max 10
using namespace std;
int arr[max] = {3,7,1,9,2,30,5,4,12,14};

void l_search(int val){
int i=0;
while(i<max){
    if(arr[i] == val){
        cout<<"value is found at position : "<<i<<endl;
        break;
    }
    else{
        i++;
    }
}
if(i>max-1){
    cout<<"value not found"<<endl;
}
}
int main(){
    int ch,c=1;
    while(c){
        cout<<"1 for searching\n2 for exit\n";
        cout<<"Enter your choice : ";
        cin>>ch;
        switch(ch){
            case 1:{
                int val;
                cout<<"Enter searching value : ";
                cin>>val;
                l_search(val);
                break;
            }
            case 2:{
                c = 0;
                break;
            }
            default:{
                cout<<"You enter wrong optiong : "<<endl;
            }
        }
    }
    return 0;
}
