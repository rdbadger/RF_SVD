clear
clc
%************************************************************************
%  DCT and PCA
%************************************************************************

paths={'1914-133440-0016.flac','dmr_clean_speech.wav', 'dmr_svd5.wav', 'dmr_6svd_1024.wav', 'dmr_7svd_1024.wav', 'dmr_8svd_1024.wav', 'dmr_9svd_1024.wav', 'dmr_svd10.wav'};
samplingRates=[1000, 2000, 4000, 8000]; 

for ii=1:length(paths)
    [s{ii}, origSamplingRate]=audioread(paths{ii});
    s{ii}=s{ii}/std(s{ii});
    sAligned{ii}=s{ii};
end

maxLag=500;

for sr=1:length(samplingRates)    
    for ii=1:length(paths)
        sDownSampled{ii}=resample(sAligned{ii}, samplingRates(sr), origSamplingRate);        
        sDownSampled{ii}=sDownSampled{ii}/std(sDownSampled{ii});
    end    
    for jj=3:length(paths)
        [C,lag] = xcorr(sDownSampled{jj},sDownSampled{2}, maxLag);
        [~, idx]=max(C);
        if lag(idx)>=0
            sAligned{jj}(1:round(lag(idx)*origSamplingRate/samplingRates(sr)))=[];
        else
            sAligned{jj}=[zeros(-round(lag(idx)*origSamplingRate/samplingRates(sr)),1); sAligned{jj}];
        end

    end    
end

for jj=3:length(paths)
    figure;
    subplot(3,1,1)
    plot(sAligned{jj})
    subplot(3,1,2)
    plot(s{2})
    subplot(3,1,3)
    plot(sAligned{jj})
end

maxAmp=0;
for jj=1:length(paths)
    if maxAmp < max(abs(sAligned{jj}))
        maxAmp=max(abs(sAligned{jj}));
    end
end

for jj=1:length(paths)
    audiowrite([paths{jj}(1:end-4), '_aligned.wav'], sAligned{jj}/(1.02*maxAmp), origSamplingRate);
end

%% stoi

paths={'1914-133440-0016_aligned.wav','dmr_clean_speech_aligned.wav', 'dmr_svd5_aligned.wav', 'dmr_6svd_1024_aligned.wav', 'dmr_7svd_1024_aligned.wav', 'dmr_8svd_1024_aligned.wav', 'dmr_9svd_1024_aligned.wav', 'dmr_svd10_aligned.wav'};
targetSamplingRate=16000;
minLength=-1;
for ii=1:length(paths)
    disp(paths{ii})
    [s{ii}, origSamplingRate]=audioread(paths{ii});
    s{ii}=resample(s{ii}, targetSamplingRate, origSamplingRate);
    if minLength==-1 || minLength > length(s{ii})
        minLength=length(s{ii});
    end
end

stoi_value=zeros(length(paths)-2,1);
snr_value=zeros(length(paths)-2,1);
for ii=3:length(paths)
    stoi_value(ii-2)=stoi(s{2}(1:minLength), s{ii}(1:minLength), targetSamplingRate)
    snr_value(ii-2)=10*log10( sum(s{2}(1:minLength).^2) / sum( (s{2}(1:minLength)-s{ii}(1:minLength)).^2 + eps) +eps);
end

figure;
plot(stoi_value)
figure;
plot(snr_value)