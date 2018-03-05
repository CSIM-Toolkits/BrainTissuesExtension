#include "itkImageFileWriter.h"
#include "itkVectorImage.h"
#include "itkVectorIndexSelectionCastImageFilter.h"
#include "itkBinaryThresholdImageFilter.h"
#include "itkStatisticsImageFilter.h"
#include "itkOtsuThresholdImageFilter.h"
#include "itkCastImageFilter.h"
#include "itkImageRegionIterator.h"
#include "itkMultipleLogisticClassificationImageFilter.h"

#include "itkPluginUtilities.h"

#include "BrainLogisticSegmentationCLP.h"

// Use an anonymous namespace to keep class types and function names
// from colliding when module is used as shared object module.  Every
// thing should be in an anonymous namespace except for the module
// entry point, e.g. main()
//
namespace
{

template <typename TPixel>
int DoIt( int argc, char * argv[], TPixel )
{
    PARSE_ARGS;

    if (doOneTissue) {
        if (selectedTissueMask>nTissues) {
            cout<<"Error: The selected tissue number is higher then the number of tissues in the image.\nThe selected tissue must be lower or equal then "<<nTissues<<"\nPlease revise this parameter."<<endl;
            return EXIT_FAILURE;
        }
    }

    typedef TPixel InputPixelType;
    typedef TPixel OutputPixelType;

    const unsigned int Dimension = 3;

    typedef itk::Image<InputPixelType,  Dimension> InputImageType;
    typedef itk::Image<unsigned char, Dimension>    LabelImageType;
    typedef itk::VectorImage<OutputPixelType, Dimension> OutputImageType;

    typedef itk::ImageFileReader<InputImageType>  ReaderType;
    typename ReaderType::Pointer reader = ReaderType::New();
    reader->SetFileName( inputVolume.c_str() );
    reader->Update();

    typedef itk::MultipleLogisticClassificationImageFilter<InputImageType>     BrainSegmentationType;
    typename BrainSegmentationType::Pointer brainSeg = BrainSegmentationType::New();
    brainSeg->SetInput(reader->GetOutput());
    brainSeg->DebugModeOn();

    //Set the number of bins.
    if (useManualBins) {
        //Use value offered from the user interface.
        brainSeg->UseManualNumberOfBinsOn();
        brainSeg->SetNumberOfBins(manualNumberOfBins);
    }

    brainSeg->SetNumberOfTissues(nTissues);

    typename InputImageType::Pointer outputImage = InputImageType::New();
    outputImage->CopyInformation(reader->GetOutput());
    outputImage->SetRegions(reader->GetOutput()->GetRequestedRegion());
    outputImage->Allocate();
    outputImage->FillBuffer(0);

    typedef itk::VectorIndexSelectionCastImageFilter<OutputImageType, InputImageType>   IndexSelectionType;
    typedef itk::StatisticsImageFilter<InputImageType>  StatisticsType;
    typedef itk::OtsuThresholdImageFilter<InputImageType,InputImageType>                OtsuThresholdType;

    typedef itk::CastImageFilter<InputImageType, LabelImageType>    CastImageType;
    typedef itk::BinaryThresholdImageFilter<InputImageType, InputImageType>             BinaryFilterType;
    typedef itk::ImageRegionIterator<InputImageType>    RegionIterator;
    RegionIterator outIt(outputImage, outputImage->GetRequestedRegion());

    typename IndexSelectionType::Pointer tissueSelector = IndexSelectionType::New();
    typename OtsuThresholdType::Pointer ostuThr = OtsuThresholdType::New();
    typename StatisticsType::Pointer stat = StatisticsType::New();
    typename CastImageType::Pointer cast = CastImageType::New();
    typename BinaryFilterType::Pointer labelMask = BinaryFilterType::New();

    tissueSelector->SetInput(brainSeg->GetOutput());

    if (doOneTissue) {
        tissueSelector->SetIndex(selectedTissueMask-1);
        tissueSelector->Update();

        cout<<"Tissue selected: "<<selectedTissueMask<<" - threshold: "<<tissueThr<<endl;
        stat->SetInput(tissueSelector->GetOutput());
        stat->Update();

        if (stat->GetMaximum()<0.95) {
            cout<<"Weighted tissue map (Max: "<<stat->GetMaximum()<<" - Min: "<<stat->GetMinimum()<<") - Ostu thresholding is being applied."<<endl; //TODO Problema com o valor adotado...tem que tirar outliers para calcular a media...

            ostuThr->SetInput(tissueSelector->GetOutput());
            ostuThr->SetInsideValue(0);
            ostuThr->SetOutsideValue(selectedTissueMask);
            ostuThr->Update();

            RegionIterator labelIt(ostuThr->GetOutput(),ostuThr->GetOutput()->GetRequestedRegion());

            outIt.GoToBegin();
            labelIt.GoToBegin();
            while (!outIt.IsAtEnd()) {
                outIt.Set(labelIt.Get());
                ++outIt;
                ++labelIt;
            }
        }else{
            cout<<"Weighted tissue map (Max: "<<stat->GetMaximum()<<" - Min: "<<stat->GetMinimum()<<")"<<endl;

            labelMask->SetInput(tissueSelector->GetOutput());
            labelMask->SetLowerThreshold(tissueThr);
            labelMask->SetInsideValue(selectedTissueMask);
            labelMask->SetOutsideValue(0);
            labelMask->Update();

            RegionIterator labelIt(labelMask->GetOutput(),labelMask->GetOutput()->GetRequestedRegion());

            outIt.GoToBegin();
            labelIt.GoToBegin();
            while (!outIt.IsAtEnd()) {
                outIt.Set(labelIt.Get());
                ++outIt;
                ++labelIt;
            }
        }
    }else{
        for (int n = 0; n < nTissues; ++n) {
            tissueSelector->SetIndex(n);
            tissueSelector->Update();

            cout<<"Tissue selected: "<<n+1<<" - threshold: "<<tissueThr<<endl;
            stat->SetInput(tissueSelector->GetOutput());
            stat->Update();

            if (stat->GetMaximum()<0.95) {
                cout<<"Weighted tissue map (Max: "<<stat->GetMaximum()<<" - Min: "<<stat->GetMinimum()<<") - Ostu thresholding is being applied."<<endl;

                ostuThr->SetInput(tissueSelector->GetOutput());
                ostuThr->SetInsideValue(0);
                ostuThr->SetOutsideValue(1);
                ostuThr->Update();

                RegionIterator labelIt(ostuThr->GetOutput(),ostuThr->GetOutput()->GetRequestedRegion());

                outIt.GoToBegin();
                labelIt.GoToBegin();
                while (!outIt.IsAtEnd()) {
                    outIt.Set(outIt.Get()+labelIt.Get());
                    ++outIt;
                    ++labelIt;
                }
            }else{
                cout<<"Weighted tissue map (Max: "<<stat->GetMaximum()<<" - Min: "<<stat->GetMinimum()<<")"<<endl;

                labelMask->SetInput(tissueSelector->GetOutput());
                labelMask->SetLowerThreshold(tissueThr);
                labelMask->SetInsideValue(n+1);
                labelMask->SetOutsideValue(0);
                labelMask->Update();

                RegionIterator labelIt(labelMask->GetOutput(),labelMask->GetOutput()->GetRequestedRegion());

                outIt.GoToBegin();
                labelIt.GoToBegin();
                while (!outIt.IsAtEnd()) {
                    if (labelIt.Get()!=static_cast<InputPixelType>(0)) {
                        outIt.Set(outIt.Get()+labelIt.Get());
                    }
                    ++outIt;
                    ++labelIt;
                }
            }
        }
    }
    cast->SetInput(outputImage);

    typedef itk::ImageFileWriter<LabelImageType> WriterType;
    typename WriterType::Pointer writer = WriterType::New();
    writer->SetFileName( outputTissue.c_str() );
    writer->SetInput( cast->GetOutput() );
    writer->SetUseCompression(1);
    writer->Update();

    return EXIT_SUCCESS;
}

} // end of anonymous namespace

int main( int argc, char * argv[] )
{
    PARSE_ARGS;

    itk::ImageIOBase::IOPixelType     pixelType;
    itk::ImageIOBase::IOComponentType componentType;

    try
    {
        itk::GetImageType(inputVolume, pixelType, componentType);

        // This filter handles all types on input, but only produces
        // signed types
        switch( componentType )
        {
        case itk::ImageIOBase::UCHAR:
            return DoIt( argc, argv, static_cast<unsigned char>(0) );
            break;
        case itk::ImageIOBase::CHAR:
            return DoIt( argc, argv, static_cast<signed char>(0) );
            break;
        case itk::ImageIOBase::USHORT:
            return DoIt( argc, argv, static_cast<unsigned short>(0) );
            break;
        case itk::ImageIOBase::SHORT:
            return DoIt( argc, argv, static_cast<short>(0) );
            break;
        case itk::ImageIOBase::UINT:
            return DoIt( argc, argv, static_cast<unsigned int>(0) );
            break;
        case itk::ImageIOBase::INT:
            return DoIt( argc, argv, static_cast<int>(0) );
            break;
        case itk::ImageIOBase::ULONG:
            return DoIt( argc, argv, static_cast<unsigned long>(0) );
            break;
        case itk::ImageIOBase::LONG:
            return DoIt( argc, argv, static_cast<long>(0) );
            break;
        case itk::ImageIOBase::FLOAT:
            return DoIt( argc, argv, static_cast<float>(0) );
            break;
        case itk::ImageIOBase::DOUBLE:
            return DoIt( argc, argv, static_cast<double>(0) );
            break;
        case itk::ImageIOBase::UNKNOWNCOMPONENTTYPE:
        default:
            std::cerr << "Unknown input image pixel component type: ";
            std::cerr << itk::ImageIOBase::GetComponentTypeAsString( componentType );
            std::cerr << std::endl;
            return EXIT_FAILURE;
            break;
        }
    }

    catch( itk::ExceptionObject & excep )
    {
        std::cerr << argv[0] << ": exception caught !" << std::endl;
        std::cerr << excep << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
