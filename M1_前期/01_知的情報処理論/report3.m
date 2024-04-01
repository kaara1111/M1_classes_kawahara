%インパルス応答のよみ取り
[audio_data,sample_rate] = audioread('record1.wav');

%インパルス応答の長さ
len_sample = length(audio_data)
x = 1:len_sample;
plot(x, audio_data);
xlabel('time(sample)');
ylabel('Amplitude');
title('Impulse Response');
figure;

%ガウス雑音を作成　参照信号u
u = randn(len_sample, 1);
plot(x, u);
xlabel('time(sample)');
ylabel('Amplitude');
title('Reference Signal');
figure;

%インパルス応答とガウス雑音の畳み込みを計算し結果を配列に格納　観測信号d
d = conv(audio_data, u,'same');


function [e, w] = LMS(u=u, d, M=64, mu=0.005)
  len_sample = length(u);
  %w_old = zeros(1,M).';
  w = zeros(1,M).';
  e(1:M-1) = zeros(M-1,1);%誤差を格納する配列　M個までは0で初期化
  tic
  for t = M:len_sample
    %e(t) = audio_data(t) - w_old.' * d(t-M+1:t);
    e(t) = d(t) - w.' * d(t-M+1:t);
    w = w + 2 * mu * e(t) * d(t-M+1:t);
    %w_old = w_new;
  end
  toc
  %ti = te - ts;
endfunction

function [E, W] = RLS(u, d, M=64, lambda=0.9, epsilon=0.0001)
  len_sample = length(u);
  W = zeros(1,M).';
  P = epsilon * eye(M);
  %P_new = zeros(M);
  E(1:M-1) = zeros(M-1,1);%誤差を格納する配列　M個までは0で初期化
  tic
  for t = M:len_sample
    g = (lambda^-1 / (1 + (lambda^-1 * d(t-M+1:t).' * P * d(t-M+1:t)))) * P * d(t-M+1:t);
    E(t) = d(t) - W.' * d(t-M+1:t);
    W = W + E(t) * g;
    P = lambda^-1 * (eye(M) - g * d(t-M+1:t).')* P;
  end
  toc
  %ti = te - ts;
end

%{
M=128;%フィルタの長さ
mu = 0.001;
[e, w] = LMS(u, d, M, mu);
%printf('elapsed time(LMS1) = %f\n', ti1);
log_values = 10 * log10(e);
x = 1:length(e);
%x = 1:6000;
plot(x, log_values);
%plot(x, log_values(1:6000));
hold on;
%}

mu = 0.01;
M=128
[e, w] = LMS(u, d, M, mu);
%printf('elapsed time(LMS1) = %f\n', ti2);
log_values = 10 * log10(e);
plot(x, log_values);
hold on;
%plot(x, log_values(1:6000));


lambda = 0.9;
epsilon = 0.1;
M = 128

[E, W] = RLS(u, d, M, lambda, epsilon);
%printf('elapsed time(RLS) = %f\n', ti3);
log_values = 10 * log10(E);
plot(x, log_values);
%plot(x, log_values(1:6000));

%{
lambda = 0.9;
epsilon = 0.1;
M = 128

[E, W] = RLS(u, d, M, lambda, epsilon);
%printf('elapsed time(RLS) = %f\n', ti3);
log_values = 10 * log10(E);
plot(x, log_values);
%}


xlabel('time(sample)');
ylabel('Power of Error');
title('Plot of Error');
%legend('RSL(lambda=0.9,epsilon=0.1,M=256)', 'RSL(lambda=0.9,epsilon=0.1,M=128)');
%legend('LMS(mu=0.001,M=128)', 'LMS(mu=0.01,M=128)');
legend('LMS(mu=0.01,M=128)', 'RLS(lambda=0.9, epsilon=0.1, M=128)');
figure;


