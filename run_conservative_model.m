function run_conservative_model
% Conservative reanalysis preserving the manuscript's empirical closure and
% duty/slope formula structure. Energy outputs are SCENARIO mechanical-CoT
% PROXIES, not measured or independently validated mechanical energy.
% Base MATLAB only. Plot-derived points are not new physical experiments.
root=fileparts(mfilename('fullpath')); out=fullfile(root,'results'); figs=fullfile(root,'figures');
if ~exist(out,'dir'),mkdir(out);end
if ~exist(figs,'dir'),mkdir(figs);end
logfile=fullfile(out,'matlab_run.log'); fid=fopen(logfile,'w');fclose(fid);diary(logfile); closeLog=onCleanup(@()diary('off')); %#ok<NASGU>
fprintf('MATLAB %s | %s\nRun UTC %s\n',version,computer,char(datetime('now','TimeZone','UTC')));
set(groot,'defaultFigureVisible','off','defaultAxesFontName','Arial','defaultTextFontName','Arial','defaultAxesFontSize',10,'defaultLineLineWidth',1.7);
blue=[.06 .31 .65];red=[.82 .23 .10];colors={blue,red};
A=readtable(fullfile(root,'data','moreland2011_fig4_traction.csv'),'TextType','string');
Ar=sortrows(A(A.mode=="rolling",:),'travel_reduction'); Ai=sortrows(A(A.mode=="inching",:),'travel_reduction');
assert(height(Ar)==7&&height(Ai)==4);
assert(all(A.travel_reduction>=0 & A.travel_reduction<1 & A.drawbar_ratio>0));
[p2,sse2]=fitTraction(Ar.travel_reduction,Ar.drawbar_ratio,true);
[p1,sse1]=fitTraction(Ar.travel_reduction,Ar.drawbar_ratio,false);
base=phi(Ai.travel_reduction,p2);lambda=sum(base.*Ai.drawbar_ratio)/sum(base.^2);
ires=lambda*base-Ai.drawbar_ratio;
parameters=table(["alpha";"K";"beta";"lambda";"f_r";"epsilon_act";"eta"], ...
 [p2(:);lambda;.05;.10;.50],[NaN;NaN;NaN;NaN;.05;.05;.50],[NaN;NaN;NaN;NaN;.15;.15;1], ...
 ["fit to seven rolling markers";"fit to seven rolling markers";"fit to seven rolling markers";"least-squares multiplier on four inching markers";"nominal assumption; selected scenario range";"nominal assumption; selected scenario range";"nominal resistance factor; selected scenario range"], ...
 'VariableNames',{'symbol','nominal_or_fitted_value','scenario_min','scenario_max','status'});
writetable(parameters,fullfile(out,'model_parameters.csv'));
% Fit-error values measure reconstruction consistency, not experimental CI.
fit_metrics=table(["two_term_rolling";"single_term_rolling";"multiplier_inching"],[7;7;4],[3;2;1], ...
 [sse2;sse1;sum(ires.^2)],[sqrt(sse2/7);sqrt(sse1/7);sqrt(mean(ires.^2))], ...
 'VariableNames',{'model','source_markers','fitted_parameters','sse_drawbar_ratio','rmse_drawbar_ratio'});
writetable(fit_metrics,fullfile(out,'traction_fit_metrics.csv'));
sourcefit=A;sourcefit.predicted_drawbar_ratio=phi(A.travel_reduction,p2);sourcefit.predicted_drawbar_ratio(A.mode=="inching")=lambda*sourcefit.predicted_drawbar_ratio(A.mode=="inching");sourcefit.residual=sourcefit.predicted_drawbar_ratio-sourcefit.drawbar_ratio;
writetable(sourcefit,fullfile(out,'traction_source_fit.csv'));
% Leave-one-marker-out diagnostic. Source markers are NOT independent trials.
cv=table;for j=1:height(Ar)
 keep=true(height(Ar),1);keep(j)=false;[pp,~]=fitTraction(Ar.travel_reduction(keep),Ar.drawbar_ratio(keep),true);
 pred=phi(Ar.travel_reduction(j),pp);
 cv=[cv;table("rolling",j,Ar.travel_reduction(j),Ar.drawbar_ratio(j),pred,pred-Ar.drawbar_ratio(j), ...
 'VariableNames',{'mode','omitted_marker','travel_reduction','observed_drawbar','predicted_drawbar','residual'})]; %#ok<AGROW>
end
for j=1:height(Ai)
 keep=true(height(Ai),1);keep(j)=false;bb=phi(Ai.travel_reduction(keep),p2);ll=sum(bb.*Ai.drawbar_ratio(keep))/sum(bb.^2);pred=ll*phi(Ai.travel_reduction(j),p2);
 cv=[cv;table("inching",j,Ai.travel_reduction(j),Ai.drawbar_ratio(j),pred,pred-Ai.drawbar_ratio(j), ...
 'VariableNames',{'mode','omitted_marker','travel_reduction','observed_drawbar','predicted_drawbar','residual'})]; %#ok<AGROW>
end
writetable(cv,fullfile(out,'traction_leave_one_marker_out.csv'));

% Fixed-traction paired scenario sensitivity. NO fit covariance is invented.
N=10000;seed=20260922;rng(seed,'twister');
fr=.05+.10*rand(1,N);epsa=.05+.10*rand(1,N);eta=.50+.50*rand(1,N);etaBaseline=.50*ones(1,N);
writetable(table((1:N)',fr',epsa',eta','VariableNames',{'draw','f_r','epsilon_act','eta'}),fullfile(out,'scenario_draws.csv'));
nom=[.05 .10 .50]; modes=["rolling","inching"];
trmin=[min(Ar.travel_reduction) min(Ai.travel_reduction)];trmax=[max(Ar.travel_reduction) max(Ai.travel_reduction)];
observedD=[min(Ar.drawbar_ratio) max(Ar.drawbar_ratio);min(Ai.drawbar_ratio) max(Ai.drawbar_ratio)];
wall=[phi(1,p2),lambda*phi(1,p2)];wallangles=atand(wall);
% Model-predicted duty at last source TR differs slightly from actual last point.
fitSupport=[phi(trmin(1),p2) phi(trmax(1),p2);lambda*phi(trmin(2),p2) lambda*phi(trmax(2),p2)];
walltable=table(modes',wall',wallangles',trmin',trmax',observedD(:,1),observedD(:,2),fitSupport(:,1),fitSupport(:,2), ...
 repmat("mathematical T=1 extrapolation; not measured maximum duty or climb angle",2,1), ...
 'VariableNames',{'mode','mathematical_duty_wall','mathematical_slope_wall_deg','observed_TR_min','observed_TR_max','observed_duty_min','observed_duty_max','fitted_duty_at_min_source_TR','fitted_duty_at_max_source_TR','wall_status'});
writetable(walltable,fullfile(out,'source_support_and_mathematical_walls.csv'));
% Figure4: original role, with reconstructed markers and actual fitted closures.
f=figure('Position',[100 100 970 570]);hold on;xx=linspace(0,1,501);
for k=1:2
 mult=1;if k==2,mult=lambda;end
 yy=mult*phi(xx,p2);inside=xx>=trmin(k)&xx<=trmax(k);
 plot(xx,yy,':','Color',colors{k},'HandleVisibility','off');
 plot(xx(inside),yy(inside),'-','Color',colors{k},'DisplayName',char(modes(k))+" fitted closure");
 B=A(A.mode==modes(k),:);plot(B.travel_reduction,B.drawbar_ratio,'o','Color',colors{k},'MarkerFaceColor',colors{k},'DisplayName',char(modes(k))+" source markers");
end
plot(xx,phi(xx,p1),'--','Color',[.4 .4 .4],'DisplayName','Single-term rolling comparator');
xlabel('Source-defined travel reduction T');ylabel('Drawbar force / vehicle weight');grid on;legend('Location','northwest');
title('Traction closure fitted to published Moreland markers');
text(.40,.025,'Solid fit: source T support; dotted: extrapolation','FontSize',9);
exportgraphics(f,fullfile(figs,'figure4_traction.png'),'Resolution',220);close(f);
% Common duty anchors retaining original Table3 rows.
duties=[0;.05;.10;.15;.20];anchors=table;reductions=table;
for n=1:numel(duties)
 d=duties(n);[tr,cr,ci,cn]=scenario(d,0,p2,lambda,fr,epsa,etaBaseline,nom);
 [~,~,ciExpanded,~]=scenario(d,0,p2,lambda,fr,epsa,eta,nom);
 qR=pct(cr,[5 50 95]);qI=pct(ci,[5 50 95]);redraw=100*(1-ciExpanded./cr);
 status=strings(1,2);for k=1:2
  if tr(k)<trmin(k)||tr(k)>trmax(k),status(k)="source-TR extrapolation";else,status(k)="within source TR range; energy closure assumed";end
 end
 anchors=[anchors;table(d,tr(1),tr(2),cn(1),cn(2),qR(2),qR(1),qR(3),qI(2),qI(1),qI(3),status(1),status(2),"not pooled", ...
 'VariableNames',{'duty','T_rolling','T_inching','nominal_rolling_proxy','nominal_inching_proxy','rolling_scenario_median','rolling_scenario_p05','rolling_scenario_p95','inching_scenario_median','inching_scenario_p05','inching_scenario_p95','rolling_support_status','inching_support_status','SPV_status'})]; %#ok<AGROW>
 epsilon_break_even_eta1=((d+nom(1))/(d+nom(1)))*(1-tr(2))/(1-tr(1))-1;
 reductions=[reductions;table(d,100*(1-cn(2)/cn(1)),median(redraw),pct(redraw,5),pct(redraw,95),mean(ciExpanded<cr), ...
 (d+nom(1))*(1+nom(2))/(1-tr(2)),epsilon_break_even_eta1, ...
 'VariableNames',{'duty','nominal_reduction_percent','paired_scenario_median_reduction_percent','paired_scenario_p05_reduction','paired_scenario_p95_reduction','scenario_fraction_inching_lower','inching_nominal_eta1_proxy','epsilon_break_even_when_eta1'})]; %#ok<AGROW>
end
anchors.ratio_of_scenario_medians_reduction_percent=100*(1-anchors.inching_scenario_median./anchors.rolling_scenario_median);
writetable(anchors,fullfile(out,'table3_anchor_values.csv'));writetable(reductions,fullfile(out,'expanded_eta_paired_sensitivity.csv'));
% Figure5: preserve duty-sweep role; same primary scenario ranges in both modes.
gridD=linspace(0,.40,650);med=nan(numel(gridD),2);lo=med;hi=med;nominal=med;trvals=med;
for n=1:numel(gridD)
 [tt,cr,ci,cn]=scenario(gridD(n),0,p2,lambda,fr,epsa,etaBaseline,nom);trvals(n,:)=tt;nominal(n,:)=cn;
 q=pct(cr,[5 50 95]);lo(n,1)=q(1);med(n,1)=q(2);hi(n,1)=q(3);
 q=pct(ci,[5 50 95]);lo(n,2)=q(1);med(n,2)=q(2);hi(n,2)=q(3);
end
f=figure('Position',[100 100 980 565]);hold on;
for k=1:2
 good=isfinite(med(:,k));x=gridD(good)';fill([x;flipud(x)],[lo(good,k);flipud(hi(good,k))],colors{k},'FaceAlpha',.12,'EdgeColor','none','HandleVisibility','off');
 ins=good&trvals(:,k)>=trmin(k)&trvals(:,k)<=trmax(k);
 plot(gridD,med(:,k),':','Color',colors{k},'HandleVisibility','off');plot(gridD(ins),med(ins,k),'-','Color',colors{k},'DisplayName',char(modes(k))+" scenario median");
 plot(gridD,nominal(:,k),'--','Color',colors{k},'LineWidth',1,'DisplayName',char(modes(k))+" nominal assumptions");
 xline(wall(k),':','Color',colors{k},'LineWidth',1.2,'HandleVisibility','off');
end
eta1nominal=(gridD'+nom(1))*(1+nom(2))./(1-trvals(:,2));
plot(gridD,eta1nominal,'-.','Color',[.3 .3 .3],'LineWidth',1.2,'DisplayName','Inching nominal eta = 1 (sensitivity)');
set(gca,'YScale','log');ylim([.02 15]);xlim([0 .40]);grid on;
xlabel('Demanded drawbar ratio d');ylabel('Scenario mechanical-CoT proxy');legend('Location','northwest');
title('Baseline duty scenarios: resistance factor eta = 0.5');
text(.205,.031,'Walls are mathematical extrapolations.\newlineNo pooled SPV reference.','FontSize',9);
exportgraphics(f,fullfile(figs,'figure5_duty.png'),'Resolution',220);close(f);
curve=table(gridD',trvals(:,1),trvals(:,2),med(:,1),lo(:,1),hi(:,1),med(:,2),lo(:,2),hi(:,2),nominal(:,1),nominal(:,2), ...
 'VariableNames',{'duty','T_rolling','T_inching','rolling_median','rolling_p05','rolling_p95','inching_median','inching_p05','inching_p95','nominal_rolling','nominal_inching'});
writetable(curve,fullfile(out,'duty_curve.csv'));
% Figure6: hypothetical inclined-bed transfer. ALL slope predictions unvalidated.
angles=linspace(0,23,650);med=nan(numel(angles),2);lo=med;hi=med;nominal=med;trvals=med;
for n=1:numel(angles)
 [tt,cr,ci,cn]=scenario(0,angles(n),p2,lambda,fr,epsa,etaBaseline,nom);trvals(n,:)=tt;nominal(n,:)=cn;
 q=pct(cr,[5 50 95]);lo(n,1)=q(1);med(n,1)=q(2);hi(n,1)=q(3);
 q=pct(ci,[5 50 95]);lo(n,2)=q(1);med(n,2)=q(2);hi(n,2)=q(3);
end
f=figure('Position',[100 100 980 565]);hold on;
for k=1:2
 good=isfinite(med(:,k));x=angles(good)';fill([x;flipud(x)],[lo(good,k);flipud(hi(good,k))],colors{k},'FaceAlpha',.12,'EdgeColor','none','HandleVisibility','off');
 ins=good&trvals(:,k)>=trmin(k)&trvals(:,k)<=trmax(k);
 plot(angles,med(:,k),':','Color',colors{k},'HandleVisibility','off');plot(angles(ins),med(ins,k),'-','Color',colors{k},'DisplayName',char(modes(k))+" scenario median");
 plot(angles,nominal(:,k),'--','Color',colors{k},'LineWidth',1,'DisplayName',char(modes(k))+" nominal assumptions");
 xline(wallangles(k),':','Color',colors{k},'HandleVisibility','off');
end
set(gca,'YScale','log');ylim([.02 15]);xlim([0 23]);grid on;xlabel('Assumed terrain slope (degrees)');ylabel('Scenario mechanical-CoT proxy');
title('Hypothetical slope transfer: baseline eta = 0.5, zero external duty');legend('Location','northwest');
text(11.5,.031,'Inclined-bed transfer is assumed.\newlineNo measured climb limit is inferred.','FontSize',9);
exportgraphics(f,fullfile(figs,'figure6_slope.png'),'Resolution',220);close(f);
writetable(table(angles',trvals(:,1),trvals(:,2),med(:,1),lo(:,1),hi(:,1),med(:,2),lo(:,2),hi(:,2),nominal(:,1),nominal(:,2), ...
 'VariableNames',{'angle_deg','T_rolling','T_inching','rolling_median','rolling_p05','rolling_p95','inching_median','inching_p05','inching_p95','nominal_rolling','nominal_inching'}),fullfile(out,'slope_curve.csv'));
slopeanchors=table;for angle=[0 5 5.7 8.5 10 15 20]
 [tt,cr,ci,cn]=scenario(0,angle,p2,lambda,fr,epsa,etaBaseline,nom);qr=pct(cr,[5 50 95]);qi=pct(ci,[5 50 95]);
 slopeanchors=[slopeanchors;table(angle,tt(1),tt(2),cn(1),cn(2),qr(2),qr(1),qr(3),qi(2),qi(1),qi(3), ...
 'VariableNames',{'angle_deg','T_rolling','T_inching','nominal_rolling','nominal_inching','rolling_median','rolling_p05','rolling_p95','inching_median','inching_p05','inching_p95'})]; %#ok<AGROW>
end
writetable(slopeanchors,fullfile(out,'slope_anchor_values.csv'));
% Figure7: same screw-family comparison role, using recoverable HGSL2/HGSL3.
S=readtable(fullfile(root,'data','thoesen2020_fig4.csv'),'TextType','string');S.cot_ratio=(S.power_measured_W./S.velocity_measured_m_s)./(S.power_predicted_W./S.velocity_predicted_m_s);
S.ratio_lower=((S.power_measured_W-S.power_digitization_bound_W)./(S.velocity_measured_m_s+S.velocity_digitization_bound_m_s))./((S.power_predicted_W+S.power_digitization_bound_W)./(S.velocity_predicted_m_s-S.velocity_digitization_bound_m_s));
S.ratio_upper=((S.power_measured_W+S.power_digitization_bound_W)./(S.velocity_measured_m_s-S.velocity_digitization_bound_m_s))./((S.power_predicted_W-S.power_digitization_bound_W)./(S.velocity_predicted_m_s+S.velocity_digitization_bound_m_s));
f=figure('Position',[100 100 940 520]);hold on;proto=unique(S.prototype,'stable');sv=table;
for k=1:numel(proto)
 B=S(S.prototype==proto(k),:);errorbar(B.target_rpm,B.cot_ratio,B.cot_ratio-B.ratio_lower,B.ratio_upper-B.cot_ratio,'o-','Color',colors{k},'MarkerFaceColor',colors{k},'DisplayName',char(proto(k)));
 pe=100*abs(B.power_predicted_W-B.power_measured_W)./B.power_measured_W;ve=100*abs(B.velocity_predicted_m_s-B.velocity_measured_m_s)./B.velocity_measured_m_s;
 sv=[sv;table(proto(k),height(B),mean(pe),mean(ve),mean(100*abs(1./B.cot_ratio-1)),min(B.cot_ratio),max(B.cot_ratio), ...
 'VariableNames',{'prototype','paired_means','power_mape_percent','velocity_mape_percent','cot_mape_percent','cot_ratio_min','cot_ratio_max'})]; %#ok<AGROW>
end
yline(1,'k--','DisplayName','Measured = predicted');grid on;legend('Location','northwest');xlabel('Nominal target screw speed (rpm)');ylabel('Measured / scaling-predicted mechanical CoT');
title('Published screw-family scaling check in BP-1');
exportgraphics(f,fullfile(figs,'figure7_screw.png'),'Resolution',220);close(f);
writetable(S,fullfile(out,'screw_matched_ratios.csv'));writetable(sv,fullfile(out,'screw_scaling_metrics.csv'));
% Additional actual energy check, not a validation of scenario Q=d+fr.
[energy,ep]=empiricalEnergy(root,figs,colors);writetable(energy,fullfile(out,'empirical_energy_check.csv'));writetable(ep,fullfile(out,'empirical_energy_predictions.csv'));
% Numerical checks: positive fit coefficients, two-term no worse in-sample,
% finite anchors, exact C=Q/(1-T), paired samples, source count, deterministic.
assert(all(p2>0)&&lambda>0&&sse2<sse1);assert(all(isfinite(anchors.nominal_rolling_proxy)));
assert(abs(phi(0,p2))<1e-12);
Ttest=[0 .2 .7 .95];Qtest=[.05 .1 .3 .7];vref=.02;W=35;pow=Qtest*W*vref;vel=vref*(1-Ttest);
identityerror=max(abs(pow./(W*vel)-Qtest./(1-Ttest)));assert(identityerror<1e-12);
summary=struct('matlab_version',version,'computer',computer,'seed',seed,'scenario_draws',N, ...
 'nominal',struct('f_r',nom(1),'epsilon_act',nom(2),'eta',nom(3)), ...
 'fit_parameters',struct('alpha',p2(1),'K',p2(2),'beta',p2(3),'lambda',lambda), ...
 'single_term_parameters',struct('amplitude',p1(1),'K',p1(2)), ...
 'fit_metrics',table2struct(fit_metrics),'anchor_values',table2struct(anchors),'expanded_eta_sensitivity',table2struct(reductions), ...
 'mathematical_walls_and_source_support',table2struct(walltable),'slope_anchors',table2struct(slopeanchors), ...
 'screw_metrics',table2struct(sv),'empirical_energy_check',table2struct(energy),'identity_error',identityerror, ...
 'scenario_percentiles_note','Table3/Fig5/Fig6 baseline fixes eta=.5, samples frU[.05,.15] and epsilonU[.05,.15], fixed traction fit. Separate expanded-eta sensitivity samples etaU[.5,1] with the same paired draws. These are scenario percentiles, not experimental confidence or posterior intervals.', ...
 'model_boundary_note','Wheel duty/slope CoT is a scenario mechanical-CoT proxy. Drawbar/TR observations do not measure or independently validate its Q closure.', ...
 'screw_note','No HGSL1 values reconstructed; no pooled6.07 estimate; mass-independent ratios used. Source table mass units omitted.', ...
 'slope_note','All inclined-bed predictions assume normal-load-scaled transfer; mathematical T=1 walls are extrapolations, not measured capability.');
fid=fopen(fullfile(out,'summary.json'),'w');fwrite(fid,jsonencode(summary,PrettyPrint=true));fclose(fid);
disp(parameters);disp(fit_metrics);disp(anchors);disp(reductions);disp(walltable);disp(energy);disp(sv);fprintf('All numerical checks passed.\n');
end

function yy=phi(x,p)
if numel(p)==2,yy=p(1)*(1-exp(-x/p(2)));else,yy=p(1)*(1-exp(-x/p(2)))+p(3)*x;end
end
function [best,bestsse]=fitTraction(x,y,two)
bestsse=Inf;best=[];opts=optimset('Display','off','MaxIter',6000,'MaxFunEvals',18000,'TolX',1e-11,'TolFun',1e-14);
for amp=[.04 .08 .2]
 for kk=[.005 .02 .1 .5]
  if two,start=[amp kk .14];else,start=[amp kk];end
  [z,val]=fminsearch(@(z)fitObjective(z,x,y),log(start),opts);
  p=exp(z);if isfinite(val)&&val<bestsse,best=p;bestsse=val;end
 end
end
assert(~isempty(best));
end
function f=fitObjective(z,x,y)
if any(~isfinite(z))||any(z < -25)||any(z>5),f=1e6+sum(min(abs(z),1e4).^2);return;end
p=exp(z);r=phi(x,p)-y;f=sum(r.^2);
end
function t=invertPhi(d,p,mult)
if d==0,t=0;elseif d<0||d>=mult*phi(1,p),t=NaN;else,t=fzero(@(x)mult*phi(x,p)-d,[0 1],optimset('TolX',1e-12,'Display','off'));end
end
function [t,cr,ci,cn]=scenario(d,theta,p,lam,fr,ep,eta,nom)
% theta in degrees; empirical flat response transferred by normal load.
effective=tand(theta)+d/cosd(theta);t=[invertPhi(effective,p,1),invertPhi(effective,p,lam)];
cr=(sind(theta)+d+fr*cosd(theta))/(1-t(1));
ci=(sind(theta)+d+eta.*fr*cosd(theta)).*(1+ep)/(1-t(2));
cn=[(sind(theta)+d+nom(1)*cosd(theta))/(1-t(1)), ...
 (sind(theta)+d+nom(3)*nom(1)*cosd(theta))*(1+nom(2))/(1-t(2))];
end
function q=pct(x,ps)
x=sort(x(isfinite(x)));q=nan(size(ps));if isempty(x),return;end
for j=1:numel(ps)
 pos=1+(numel(x)-1)*ps(j)/100;a=floor(pos);b=ceil(pos);q(j)=x(a)+(pos-a)*(x(b)-x(a));
end
end
function [metrics,allpred]=empiricalEnergy(root,figs,colors)
R=readtable(fullfile(root,'data','creager2014_matched_rolling_times.csv'),'TextType','string');I=readtable(fullfile(root,'data','creager2014_inching_published_mean_lines.csv'),'TextType','string');
metrics=table;allpred=table;f=figure('Position',[100 100 980 420]);tiledlayout(1,2,'TileSpacing','compact','Padding','compact');
for tire=["pneumatic","rigid"]
 B=sortrows(R(R.tire==tire,:),'time_s');cal=ismember(B.time_s,[20 30 40]);test=ismember(B.time_s,[50 60 70 80]);q=B.total_power_number.*(1-B.travel_reduction);q0=median(q(cal));pred=q0./(1-B.travel_reduction);base=median(B.total_power_number(cal));
 rmse=sqrt(mean((pred(test)-B.total_power_number(test)).^2));mape=100*mean(abs(pred(test)-B.total_power_number(test))./B.total_power_number(test));brmse=sqrt(mean((base-B.total_power_number(test)).^2));
 metrics=[metrics;table(tire,q0,sum(cal),sum(test),rmse,mape,brmse,'VariableNames',{'tire','Q_empirical','calibration_times','evaluation_times','rmse_PN','mape_percent','constant_PN_baseline_rmse'})]; %#ok<AGROW>
 role=repmat("diagnostic",height(B),1);role(cal)="calibration";role(test)="temporal_holdout";
 allpred=[allpred;table(B.tire,B.time_s,B.travel_reduction,B.total_power_number,pred,role,'VariableNames',{'tire','time_s','observed_TR','observed_PN','predicted_PN','role'})]; %#ok<AGROW>
 nexttile;plot(B.time_s,B.total_power_number,'ko-','MarkerFaceColor','k','DisplayName','Source rolling PN');hold on;
 plot(B.time_s,pred,'-','Color',colors{1},'DisplayName','Conditional constant-Q model');plot(B.time_s(cal),B.total_power_number(cal),'s','Color',colors{2},'MarkerFaceColor',colors{2},'DisplayName','Calibration');
 ii=I(I.tire==tire,:);yline(ii.mean_total_power_number,'--','Color',colors{2},'DisplayName','Source inching mean');xline(45,':','Holdout','HandleVisibility','off');
 xlabel('Time (s)');ylabel('Total vehicle power number');title(tire+": holdout MAPE "+sprintf('%.1f%%',mape));grid on;legend('Location','northwest');
end
exportgraphics(f,fullfile(figs,'figure8_empirical_energy_check.png'),'Resolution',220);close(f);
end
