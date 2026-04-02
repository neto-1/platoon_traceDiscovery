clear

% Define table 
Schema = {'Edges';'Vehicles';'Iteration';'STime';'RTime';'GTime';'ITime';'VShortestPath';'SumTime';'SumSP';'SumPSP';'UVehicles';'Ing';'Outg';'Optimum'; 'OptimumTime'};
T = table(0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0);
T.Properties.VariableNames = Schema;

%%% link to current folder
% pwd;
% currentFolder = pwd;

%%%%%% gerrits pc
%files = getFiles('C:\Users\db-admin\Documents\tests\res\LargeResults');

%%%%%% dimas pc
%files = getFiles('C:\Users\Dietrich\Desktop\res\ResultsLarge');

files = getFiles('C:\Users\Dietrich\Desktop\res\LargeResultsIters');




for n = 1:numel(files)
    file = files(n);
    fid = fopen(char(file));

    % first line of txt file
    tline = fgets(fid);
    i = 1;
    A=zeros(1,16);
    while ischar(tline)
        A(i) = str2double(tline);
        %disp(tline);
        tline = fgets(fid);
        i=1+i;
    end
    % add new row with data 
    %A(i+1)=-1;
    C = num2cell(A);
    T(n:n,:)= C;
    fclose(fid);
end

%close the opened txt files (or matlab crash
fclose('all');

T = sortrows(T,'Edges');
%T = sortrows(T,'Vehicles');

%vars = {'Optimum','OptimumTime'};
%unique(T, vars)

%T{:,{'Edges','GTime'}};

XEdges = T{:,{'Edges'}};
XEdges = unique(XEdges);
[e,e2]=size(XEdges);


YVehicles = T{:,{'Vehicles'}};
YVehicles = unique(YVehicles);




[v,v2]=size(YVehicles);
%vars = {'Edges','Vehicles','Iteration','STime','RTime','GTime','ITime'};
vars = {'STime','RTime','GTime','ITime'};
AT=zeros(e,v);



varsTime = {'SumTime'};
T;

SchemaR = {'Edges';'Vehicles';'Mean';'SD'};
R = table;
%R.Properties.VariableNames = SchemaR;





size(XEdges)
size(YVehicles)


Res=zeros(e,v);
ResSd=zeros(e,v);

%A=zeros(size(XEdges),size(YVehicles));

for i = 1:size(XEdges)
    for d = 1:size(YVehicles)
        rows = T.Edges == XEdges(i) & T.Vehicles == YVehicles(d);
        table2array(T(rows, vars));
      
        (transpose(table2array(T(rows, vars))));
        T(rows, varsTime) = array2table(transpose(sum(transpose(table2array(T(rows, vars))))));
       
        sd = std(table2array(T(rows, varsTime)));
        mn = mean(table2array(T(rows, varsTime)));
        RET = array2table([XEdges(i), YVehicles(d), mn, sd]);
        RET.Properties.VariableNames = SchemaR;
        R = [R;RET];
        Res(i,d) = mn;
        ResSd(i,d) = sd;
    end
   
    %Res(i) = transpose(R.Mean)
    %table2array(R.Mean)
    
%    XEdges(i);
%    rows = T.Edges == XEdges(i);
%    Ma = sum(transpose(table2array(T(rows, vars))));
% 
%   % AT(i,:) = sort(Ma);
%    size(AT);
%    size(Ma);
   
   %str = '~~'
   %size(transpose(table2array(T(rows, vars))))
   % AT(i) =  T(rows, vars)    
end

R

%Res = sort(Res,2);
%ResSd = sort(ResSd, 2);

b = bar(XEdges,Res);

set(b(7),'FaceColor',[70 51 126] ./ 255);
set(b(6),'FaceColor',[54 92 141] ./ 255);
set(b(5),'FaceColor',[39 127 142] ./ 255);
set(b(4),'FaceColor',[31 161 135] ./ 255);
set(b(3),'FaceColor',[74 193 109] ./ 255);
set(b(2),'FaceColor',[159 218 58] ./ 255);
set(b(1),'FaceColor',[253 231 37] ./ 255);

set(b, 'LineStyle','none');
set(gca,'YScale','log');
hold on
ba = bar(XEdges, ResSd, 'EdgeColor',[1 1 1], 'LineWidth',1);

set(ba(7),'FaceColor',[70 51 126] ./ 255);
set(ba(6),'FaceColor',[54 92 141] ./ 255);
set(ba(5),'FaceColor',[39 127 142] ./ 255);
set(ba(4),'FaceColor',[31 161 135] ./ 255);
set(ba(3),'FaceColor',[74 193 109] ./ 255);
set(ba(2),'FaceColor',[159 218 58] ./ 255);
set(ba(1),'FaceColor',[253 231 37] ./ 255);



%set(b(1),'FaceAlpha',0.2)

%[l,l1]=size(XEdges)
%AT = [9321.321]
% format shortG
% Z = T{:,{'GTime'}};
%b = bar(XEdges,AT);
% set(gca,'YScale','log');
% 
% 
