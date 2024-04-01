%インパルス応答のよみ取り
[audio_data,sample_rate] = audioread('AKG-K240-L.wav');
%plot(audio_data);%インパルス応答のグラフ
%disp('audiodata');
%インパルス応答の情報　1行の状態
len_sample = length(audio_data);

%ガウス雑音の情報を読み込み配列に格納　参照信号u_t
u = randn(len_sample, 1);
%plot(u_t);%参照信号のグラフ
%disp('gauss');

%インパルス応答とガウス雑音の畳み込みを計算し結果を配列に格納　観測信号d_t
#sameで指定することで畳み込みの結果がu_tと同じ長さになる　デフォルトでは16383+16383-1=32765となり不適
d = conv(audio_data, u, 'same');
%plot(d_t);%観測信号のグラフ
%disp('dt');

function [e, w, time] = LMS(u=u, d, M=64, mu=0.005)
  len_sample = length(u);
  %w_old = zeros(1,M).';
  w = zeros(1,M).';
  e(1:M-1) = zeros(M-1,1);%誤差を格納する配列　M個までは0で初期化
  tic();
  for t = M:len_sample
    %e(t) = audio_data(t) - w_old.' * d(t-M+1:t);
    e(t) = d(t) - w.' * d(t-M+1:t);
    w = w + 2 * mu * e(t) * d(t-M+1:t);
    %w_old = w_new;
  end
  elapsed_time = toc ();
endfunction

M=128;%フィルタの長さ
mu = 0.001;
[e, w, time] = LMS(u, d, M, mu)
%{
w_old = zeros(1,M).';
w_new = zeros(1,M).';
e(1:M-1) = zeros(M-1,1);%誤差を格納する配列　M個までは0で初期化
tic();
for t = M:len_sample
  e(t) = audio_data(t) - w_old.' * d(t-M+1:t);
  w_new = w_old + 2 * mu * e(t) * d(t-M+1:t);
  w_old = w_new;
end
elapsed_time = toc ();
%}

disp('elapsed_time');
disp(time);

log_values = 10 * log10(e);

x = 1:length(e);
plot(x, log_values);
xlabel('time(sample)');
ylabel('Log Value');
title('Plot of Error');
hold on;

mu = 0.01;
%{
w_old = zeros(1,M).';
w_new = zeros(1,M).';
e(1:M-1) = zeros(M-1,1);%誤差を格納する配列　M個までは0で初期化
for t = M:len_sample
  e(t) = audio_data(t) - w_old.' * d(t-M+1:t);
  w_new = w_old + 2 * mu * e(t) * d(t-M+1:t);
  w_old = w_new;
end
%}
[e, w, time] = LMS(u, d, M, mu)

log_values = 10 * log10(e);

x = 1:length(e);
plot(x, log_values);
legend('mu=0.001', 'mu=0.01')
figure;
